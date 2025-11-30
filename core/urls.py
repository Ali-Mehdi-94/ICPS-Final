from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    StudentViewSet,
    RegistrationViewSet,
    CourseProviderViewSet,
    FieldViewSet,
    LevelViewSet,
    me,
    CeoSummaryView,
    SalesSummaryView,
    OpsSummaryView,
    ProQualAdminSummaryView,
    ProQualRegistrationViewSet,
    ProQualAssignOpsView,
    ProQualSetPortalDateView,
    ProQualOpsListView,
    UnitTaskCompleteView,
    InstallmentPayView,
    OverduePaymentsView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'registrations', RegistrationViewSet)
router.register(r'providers', CourseProviderViewSet)
router.register(r'fields', FieldViewSet)
router.register(r'levels', LevelViewSet)
router.register(r'proqual/registrations', ProQualRegistrationViewSet, basename='proqual-registration')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', me),
    # Dashboards
    path('dashboard/ceo/summary/', CeoSummaryView.as_view(), name='ceo-summary'),
    path('dashboard/sales/summary/', SalesSummaryView.as_view(), name='sales-summary'),
    path('dashboard/ops/summary/', OpsSummaryView.as_view(), name='ops-summary'),
    path('dashboard/proqual/summary/', ProQualAdminSummaryView.as_view(), name='proqual-admin-summary'),
    path('dashboard/payments/overdue/', OverduePaymentsView.as_view(), name='overdue-payments'),
    # ProQual Admin Actions
    path('proqual/registrations/<int:pk>/assign-ops/', ProQualAssignOpsView.as_view(), name='proqual-assign-ops'),
    path('proqual/registrations/<int:pk>/set-portal-date/', ProQualSetPortalDateView.as_view(), name='proqual-set-portal-date'),
    path('proqual/ops-list/', ProQualOpsListView.as_view(), name='proqual-ops-list'),
    # Actions
    path('units/<int:pk>/complete/', UnitTaskCompleteView.as_view(), name='unit-complete'),
    path('installments/<int:pk>/pay/', InstallmentPayView.as_view(), name='installment-pay'),
]
