import logging
from .permissions import IsCEO, IsSales, IsOps, IsProQualAdmin
from django.db.models import Q
from django.db import transaction

from .utils import next_ops_user

from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.utils import timezone
from .models import CustomUser, Student, Registration, CourseProvider, Field, Level, UnitTask, PaymentInstallment
from .serializers import (
    UserSerializer,
    StudentSerializer,
    RegistrationSerializer,
    CourseProviderSerializer,
    FieldSerializer,
    LevelSerializer,
)
from .dashboard import get_ceo_summary, get_sales_summary, get_ops_summary, get_proqual_admin_summary

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseProviderViewSet(viewsets.ModelViewSet):
    queryset = CourseProvider.objects.all()
    serializer_class = CourseProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        provider_id = self.request.query_params.get("provider")
        if provider_id:
            try:
                provider_id = int(provider_id)
                qs = qs.filter(provider_id=provider_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid provider_id in query params: {provider_id}")
                # Return empty queryset for invalid input
                return qs.none()
        return qs

class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        provider_id = self.request.query_params.get("provider")
        field_id = self.request.query_params.get("field")
        
        # If provider & field given, show levels that have program templates
        # OR all levels if no templates exist (to allow registration even without templates)
        if provider_id and field_id:
            try:
                provider_id = int(provider_id)
                field_id = int(field_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid provider_id or field_id in query params: provider={provider_id}, field={field_id}")
                return qs.none()
            
            from .models import ProgramTemplate
            # First try to get levels with templates
            template_levels = qs.filter(
                programtemplate__provider_id=provider_id,
                programtemplate__field_id=field_id,
            ).distinct()
            # If we have template levels, return those. Otherwise return all levels.
            # This allows ProQual and other providers to work even without templates.
            if template_levels.exists():
                return template_levels
            # If no templates exist, return all levels (user can still register)
            return qs
        return qs

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "CEO":
            return Student.objects.all()
        elif user.role == "Sales":
            return Student.objects.filter(registration__registered_by=user)
        elif user.role == "Ops":
            return Student.objects.filter(registration__assigned_to=user)
        return Student.objects.none()

class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.select_related(
        'student', 'provider', 'field', 'level', 'registered_by', 'assigned_to'
    ).prefetch_related('tasks', 'payment_plan__installments')
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        
        # Role-based filtering
        if user.role == "CEO":
            return qs  # CEO sees all
        elif user.role == "Sales":
            return qs.filter(registered_by=user)
        elif user.role == "Ops":
            return qs.filter(assigned_to=user)
        return qs.none()

    def perform_create(self, serializer):
        # Check if this is a ProQual registration
        provider = serializer.validated_data.get("provider")
        is_proqual = provider and provider.name.lower() == "proqual"
        
        # If client didn't provide assigned_to, do round-robin (skip for ProQual)
        assigned_user = serializer.validated_data.get("assigned_to")
        if assigned_user is None and not is_proqual:
            # Only use round-robin for non-ProQual registrations
            try:
                assigned_user = next_ops_user()
                if assigned_user is None:
                    logger.warning("No Ops users available for round-robin assignment")
            except (ValueError, Exception) as e:
                logger.error(f"Error in round-robin assignment: {str(e)}")
                assigned_user = None  # will save as null if truly no Ops
        elif assigned_user is None and is_proqual:
            # ProQual requires manual assignment - don't auto-assign
            logger.info("ProQual registration created without assigned_to - requires manual assignment")
        
        try:
            with transaction.atomic():
                serializer.save(registered_by=self.request.user, assigned_to=assigned_user)
        except Exception as e:
            logger.error(f"Error creating registration: {str(e)}")
            raise DRFValidationError(f"Failed to create registration: {str(e)}")

    def perform_update(self, serializer):
        # Enforce Ops for assigned_to on updates too
        assigned_user = serializer.validated_data.get("assigned_to")
        if assigned_user is None:
            # if they blank it, we can reassign next Ops or keep as-is
            try:
                assigned_user = next_ops_user()
                if assigned_user is None:
                    logger.warning("No Ops users available for round-robin assignment during update")
            except (ValueError, Exception) as e:
                logger.error(f"Error in round-robin assignment during update: {str(e)}")
                assigned_user = None
        
        try:
            with transaction.atomic():
                serializer.save(assigned_to=assigned_user)
        except Exception as e:
            logger.error(f"Error updating registration: {str(e)}")
            raise DRFValidationError(f"Failed to update registration: {str(e)}")
        
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    """Get current authenticated user information."""
    try:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error retrieving user info: {str(e)}")
        return Response(
            {"detail": "Failed to retrieve user information."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CeoSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCEO]

    def get(self, request):
        """Get CEO dashboard summary."""
        try:
            data = get_ceo_summary()
            return Response(data)
        except Exception as e:
            logger.error(f"Error generating CEO summary: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to generate CEO dashboard summary."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SalesSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSales]

    def get(self, request):
        """Get Sales dashboard summary for the current user."""
        try:
            data = get_sales_summary(request.user)
            return Response(data)
        except Exception as e:
            logger.error(f"Error generating Sales summary for user {request.user.id}: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to generate Sales dashboard summary."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OpsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOps]

    def get(self, request):
        """
        Return operations dashboard metrics for the logged-in Ops user.
        """
        try:
            data = get_ops_summary(request.user)
            return Response(data)
        except Exception as e:
            logger.error(f"Error generating Ops summary for user {request.user.id}: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to generate Operations dashboard summary."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnitTaskCompleteView(APIView):
    """
    POST /api/units/<id>/complete/
    Marks a UnitTask as DONE.
    - Ops: can only complete tasks assigned to themselves.
    - CEO: can complete any task.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        """Mark a unit task as completed."""
        try:
            task = UnitTask.objects.select_related("registration", "assigned_to").get(pk=pk)
        except UnitTask.DoesNotExist:
            return Response(
                {"detail": "Task not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid task ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        user_role = getattr(user, "role", "")

        # If Ops, enforce that it's their own task
        if user_role == "Ops" and task.assigned_to_id != user.id:
            return Response(
                {"detail": "You can only complete your own tasks."},
                status=status.HTTP_403_FORBIDDEN
            )

        # CEO and Ops (on their own tasks) can complete
        if user_role not in ("Ops", "CEO"):
            return Response(
                {"detail": "Only Ops or CEO can complete tasks."},
                status=status.HTTP_403_FORBIDDEN
            )

        if task.status == "DONE":
            return Response(
                {"detail": "Task is already marked as completed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                task.status = "DONE"
                task.completed_at = timezone.now()
                task.save()

                # Update ops incentives if coursework is completed on time
                try:
                    task.registration.update_ops_incentive_status()
                except Exception as e:
                    # Log the error but don't break the API
                    logger.error(
                        f"Failed to update ops incentive for registration {task.registration_id}: {str(e)}",
                        exc_info=True
                    )
                
                # Send notifications based on provider type
                try:
                    from .notifications import notify_proqual_unit_completed, notify_ceo_unit_completed
                    if task.registration.is_proqual:
                        notify_proqual_unit_completed(task)
                    else:
                        notify_ceo_unit_completed(task)
                except Exception as e:
                    logger.error(f"Failed to send unit completion notification: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"Error completing task {pk}: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to complete task. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"detail": "Task marked as completed.", "task_id": task.id, "completed_at": task.completed_at},
            status=status.HTTP_200_OK
        )


class InstallmentPayView(APIView):
    """
    POST /api/installments/<id>/pay/
    Marks a PaymentInstallment as paid (today's date by default).
    Sales & CEO can use this.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        """Mark a payment installment as paid."""
        try:
            inst = PaymentInstallment.objects.select_related("plan__registration").get(pk=pk)
        except PaymentInstallment.DoesNotExist:
            return Response(
                {"detail": "Installment not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid installment ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        user_role = getattr(user, "role", "")

        if user_role not in ("Sales", "CEO"):
            return Response(
                {"detail": "Only Sales or CEO can mark payments as paid."},
                status=status.HTTP_403_FORBIDDEN
            )

        if inst.paid_at:
            return Response(
                {"detail": "Installment already marked as paid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                today = timezone.localdate()
                inst.paid_at = today
                inst.save()

                # Update sales incentive status for the registration
                try:
                    inst.plan.registration.update_sales_incentive_status()
                except Exception as e:
                    # Log the error but don't break the API
                    logger.error(
                        f"Failed to update sales incentive for registration {inst.plan.registration_id}: {str(e)}",
                        exc_info=True
                    )
        except Exception as e:
            logger.error(f"Error marking installment {pk} as paid: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to mark installment as paid. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "detail": f"Installment marked as paid on {today}.",
                "installment_id": inst.id,
                "paid_at": inst.paid_at,
                "amount": str(inst.amount)
            },
            status=status.HTTP_200_OK
        )


class ProQualAdminSummaryView(APIView):
    """ProQual Admin Dashboard Summary"""
    permission_classes = [permissions.IsAuthenticated, IsProQualAdmin]

    def get(self, request):
        """Get ProQual admin dashboard summary."""
        try:
            data = get_proqual_admin_summary()
            return Response(data)
        except Exception as e:
            logger.error(f"Error generating ProQual admin summary: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to generate ProQual admin dashboard summary."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProQualRegistrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProQual registrations - only accessible by ProQualAdmin.
    Allows creating, viewing, and updating ProQual registrations.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsProQualAdmin]

    def get_queryset(self):
        """Get all ProQual registrations"""
        from .models import CourseProvider
        try:
            proqual_provider = CourseProvider.objects.get(name__iexact="ProQual")
            return Registration.objects.filter(provider=proqual_provider).select_related(
                'student', 'provider', 'field', 'level', 'registered_by', 'assigned_to'
            ).prefetch_related('tasks', 'payment_plan__installments')
        except CourseProvider.DoesNotExist:
            return Registration.objects.none()

    def perform_create(self, serializer):
        """Create ProQual registration - no auto-assignment"""
        try:
            with transaction.atomic():
                # ProQual registrations don't get auto-assigned
                serializer.save(registered_by=self.request.user, assigned_to=None)
        except Exception as e:
            logger.error(f"Error creating ProQual registration: {str(e)}")
            raise DRFValidationError(f"Failed to create ProQual registration: {str(e)}")


class ProQualAssignOpsView(APIView):
    """
    POST /api/proqual/registrations/<id>/assign-ops/
    Manually assign an Ops team member to a ProQual registration.
    """
    permission_classes = [permissions.IsAuthenticated, IsProQualAdmin]

    def post(self, request, pk):
        """Assign Ops team member to ProQual registration"""
        try:
            from .models import CourseProvider, CustomUser
            
            # Get ProQual provider
            try:
                proqual_provider = CourseProvider.objects.get(name__iexact="ProQual")
            except CourseProvider.DoesNotExist:
                return Response(
                    {"detail": "ProQual provider not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get registration
            try:
                registration = Registration.objects.get(pk=pk, provider=proqual_provider)
            except Registration.DoesNotExist:
                return Response(
                    {"detail": "ProQual registration not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get ops_user_id from request
            ops_user_id = request.data.get('ops_user_id')
            if not ops_user_id:
                return Response(
                    {"detail": "ops_user_id is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify user is Ops
            try:
                ops_user = CustomUser.objects.get(id=ops_user_id, role="Ops", is_active=True)
            except CustomUser.DoesNotExist:
                return Response(
                    {"detail": "Invalid Ops user ID or user is not an active Ops member."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Assign and save
            with transaction.atomic():
                registration.assigned_to = ops_user
                registration.save(update_fields=['assigned_to'])
                
                # If portal_allotment_date is set, regenerate tasks
                if registration.portal_allotment_date:
                    from .services import create_units_for_registration
                    create_units_for_registration(registration)
            
            # Send notification to ProQual ops team
            try:
                from .notifications import notify_proqual_ops_assigned
                notify_proqual_ops_assigned(registration)
            except Exception as e:
                logger.error(f"Failed to send ProQual ops assignment notification: {str(e)}", exc_info=True)
            
            return Response(
                {
                    "detail": f"Ops team member {ops_user.username} assigned successfully.",
                    "registration_id": registration.id,
                    "assigned_to": ops_user.id,
                    "assigned_to_username": ops_user.username
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error assigning Ops to ProQual registration {pk}: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to assign Ops team member."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProQualSetPortalDateView(APIView):
    """
    POST /api/proqual/registrations/<id>/set-portal-date/
    Set the portal allotment date for a ProQual registration.
    This will trigger the 32-week timeline to start.
    """
    permission_classes = [permissions.IsAuthenticated, IsProQualAdmin]

    def post(self, request, pk):
        """Set portal allotment date and start timeline"""
        try:
            from .models import CourseProvider
            from datetime import datetime
            
            # Get ProQual provider
            try:
                proqual_provider = CourseProvider.objects.get(name__iexact="ProQual")
            except CourseProvider.DoesNotExist:
                return Response(
                    {"detail": "ProQual provider not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get registration
            try:
                registration = Registration.objects.get(pk=pk, provider=proqual_provider)
            except Registration.DoesNotExist:
                return Response(
                    {"detail": "ProQual registration not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get portal_allotment_date from request
            portal_date_str = request.data.get('portal_allotment_date')
            if not portal_date_str:
                return Response(
                    {"detail": "portal_allotment_date is required (YYYY-MM-DD format)."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                portal_date = datetime.strptime(portal_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set portal date and regenerate tasks
            with transaction.atomic():
                registration.portal_allotment_date = portal_date
                registration.save(update_fields=['portal_allotment_date'])
                
                # Regenerate tasks with new start date
                from .services import create_units_for_registration
                create_units_for_registration(registration)
            
            # Send notification about portal allotment
            try:
                from .notifications import notify_proqual_portal_allotted
                notify_proqual_portal_allotted(registration)
            except Exception as e:
                logger.error(f"Failed to send ProQual portal allotment notification: {str(e)}", exc_info=True)
            
            return Response(
                {
                    "detail": f"Portal allotment date set to {portal_date}. Timeline started.",
                    "registration_id": registration.id,
                    "portal_allotment_date": portal_date.isoformat(),
                    "tasks_created": registration.tasks.count()
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error setting portal date for ProQual registration {pk}: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to set portal allotment date."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProQualOpsListView(APIView):
    """
    GET /api/proqual/ops-list/
    Get list of all active Ops team members for assignment.
    """
    permission_classes = [permissions.IsAuthenticated, IsProQualAdmin]

    def get(self, request):
        """Get list of active Ops users"""
        try:
            ops_users = CustomUser.objects.filter(role="Ops", is_active=True).order_by("username")
            ops_list = [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
                for user in ops_users
            ]
            return Response({"ops_users": ops_list}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving Ops list: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to retrieve Ops team list."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OverduePaymentsView(APIView):
    """
    GET /dashboard/payments/overdue/
    Returns a list of all overdue payment installments.
    Accessible by CEO and Sales.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role not in ("CEO", "Sales"):
            return Response({"detail": "Not authorized."}, status=403)
            
        today = timezone.localdate()
        overdue = PaymentInstallment.objects.filter(
            paid_at__isnull=True,
            due_date__lt=today
        ).select_related('plan__registration__student', 'plan__registration__provider', 'plan__registration__registered_by')
        
        if user.role == "Sales":
            overdue = overdue.filter(plan__registration__registered_by=user)
            
        data = []
        for inst in overdue:
            data.append({
                "id": inst.id,
                "student_name": inst.plan.registration.student.name,
                "provider": inst.plan.registration.provider.name,
                "amount": inst.amount,
                "due_date": inst.due_date,
                "days_overdue": (today - inst.due_date).days,
                "registered_by": inst.plan.registration.registered_by.username if inst.plan.registration.registered_by else "Unknown"
            })
            
        return Response(data)

