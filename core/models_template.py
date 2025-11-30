
from django.db import models
from .models import CourseProvider, Level

class ProgramTemplate(models.Model):
    QUAL_TYPE_CHOICES = (
        ("award", "Award"),
        ("certificate", "Certificate"),
        ("diploma", "Diploma"),
        ("extended", "Extended Diploma"),
    )

    provider = models.ForeignKey(CourseProvider, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    # Optional classification (you can leave blank for ProQual)
    qual_type = models.CharField(max_length=20, choices=QUAL_TYPE_CHOICES, blank=True, null=True)

    # Optional variant name for exceptions (e.g., “OHS”, “Project Management”)
    variant_name = models.CharField(max_length=100, blank=True, null=True)

    # Defaults for planning
    default_unit_count = models.PositiveIntegerField()
    duration_months = models.PositiveIntegerField()  # total planned months

    # ProQual-style phase
    has_forms_phase = models.BooleanField(default=False)
    forms_weeks = models.PositiveIntegerField(default=0)

    def __str__(self):
        parts = [self.provider.name, f"Level {self.level.number}"]
        if self.variant_name:
            parts.append(self.variant_name)
        if self.qual_type:
            parts.append(self.get_qual_type_display())
        return " • ".join(parts)

