"""
Management command to seed default OTHM and ProQual program templates.

Usage:
    python manage.py seed_programs
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    CourseProvider, Field, Level, ProgramTemplate, UnitTemplate
)


class Command(BaseCommand):
    help = 'Seed default OTHM and ProQual program templates with units'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing templates before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing templates...'))
            ProgramTemplate.objects.all().delete()
            UnitTemplate.objects.all().delete()
            Field.objects.all().delete()
            CourseProvider.objects.all().delete()
            Level.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Seeding program templates...'))

        # Create Course Providers
        othm, _ = CourseProvider.objects.get_or_create(name='OTHM')
        proqual, _ = CourseProvider.objects.get_or_create(name='ProQual')
        self.stdout.write(self.style.SUCCESS('Created providers: OTHM, ProQual'))

        # Create Levels
        levels = {}
        for level_num in [3, 4, 5, 6, 7]:
            levels[level_num], _ = Level.objects.get_or_create(number=level_num)
        self.stdout.write(self.style.SUCCESS(f'Created levels: {list(levels.keys())}'))

        # Create Fields
        fields = {}
        
        # OTHM Fields
        fields['othm_ohs'], _ = Field.objects.get_or_create(name='OHS', provider=othm)
        fields['othm_business'], _ = Field.objects.get_or_create(name='Business', provider=othm)
        fields['othm_it'], _ = Field.objects.get_or_create(name='IT', provider=othm)
        fields['othm_project'], _ = Field.objects.get_or_create(name='Project Management', provider=othm)
        
        # ProQual Fields
        fields['proqual_ohs'], _ = Field.objects.get_or_create(name='OHS', provider=proqual)
        fields['proqual_business'], _ = Field.objects.get_or_create(name='Business', provider=proqual)
        
        self.stdout.write(self.style.SUCCESS('Created fields for OTHM and ProQual'))

        # ===== OTHM TEMPLATES =====
        self.stdout.write(self.style.SUCCESS('\n--- Creating OTHM Templates ---'))
        
        # OTHM: Level 3-7 Standard (6 units) - Diploma
        for level_num in [3, 4, 5, 6, 7]:
            # Skip Level 6 OHS (will be created separately with 7 units)
            if level_num == 6:
                continue
            
            # Skip Level 7 Project Management (will be created separately with 5 units)
            if level_num == 7:
                continue
            
            field = fields['othm_business']  # Default to Business
            template, created = ProgramTemplate.objects.get_or_create(
                provider=othm,
                field=field,
                level=levels[level_num],
                qualification_type='diploma',
                defaults={
                    'name': f'OTHM Level {level_num} Diploma',
                    'duration_weeks': 16,  # 4 months
                    'default_unit_count': 6,
                }
            )
            if created:
                self._create_othm_units(template, 6)
                self.stdout.write(self.style.SUCCESS(f'  Created: {template}'))

        # OTHM: Level 6 OHS (7 units) - Diploma
        template, created = ProgramTemplate.objects.get_or_create(
            provider=othm,
            field=fields['othm_ohs'],
            level=levels[6],
            qualification_type='diploma',
            defaults={
                'name': 'OTHM Level 6 OHS Diploma',
                'duration_weeks': 16,
                'default_unit_count': 7,
            }
        )
        if created:
            self._create_othm_units(template, 7)
            self.stdout.write(self.style.SUCCESS(f'  Created: {template}'))

        # OTHM: Level 7 Project Management (5 units) - Diploma
        template, created = ProgramTemplate.objects.get_or_create(
            provider=othm,
            field=fields['othm_project'],
            level=levels[7],
            qualification_type='diploma',
            defaults={
                'name': 'OTHM Level 7 Project Management Diploma',
                'duration_weeks': 16,
                'default_unit_count': 5,
            }
        )
        if created:
            self._create_othm_units(template, 5)
            self.stdout.write(self.style.SUCCESS(f'  Created: {template}'))

        # OTHM: Level 5 Extended (12 units) - Extended Diploma
        template, created = ProgramTemplate.objects.get_or_create(
            provider=othm,
            field=fields['othm_business'],
            level=levels[5],
            qualification_type='extended',
            defaults={
                'name': 'OTHM Level 5 Extended Diploma',
                'duration_weeks': 16,
                'default_unit_count': 12,
            }
        )
        if created:
            self._create_othm_units(template, 12)
            self.stdout.write(self.style.SUCCESS(f'  Created: {template}'))

        # OTHM: Awards (2 units)
        for level_num in [3, 4, 5, 6, 7]:
            template, created = ProgramTemplate.objects.get_or_create(
                provider=othm,
                field=fields['othm_business'],
                level=levels[level_num],
                qualification_type='award',
                defaults={
                    'name': f'OTHM Level {level_num} Award',
                    'duration_weeks': 16,
                    'default_unit_count': 2,
                }
            )
            if created:
                self._create_othm_units(template, 2)
                self.stdout.write(self.style.SUCCESS(f'  Created: {template}'))

        # OTHM: Certificates (3 units)
        for level_num in [3, 4, 5, 6, 7]:
            template, created = ProgramTemplate.objects.get_or_create(
                provider=othm,
                field=fields['othm_business'],
                level=levels[level_num],
                qualification_type='certificate',
                defaults={
                    'name': f'OTHM Level {level_num} Certificate',
                    'duration_weeks': 16,
                    'default_unit_count': 3,
                }
            )
            if created:
                self._create_othm_units(template, 3)
                self.stdout.write(self.style.SUCCESS(f'  Created: {template}'))

        # ===== PROQUAL TEMPLATES =====
        self.stdout.write(self.style.SUCCESS('\n--- Creating ProQual Templates ---'))
        
        # ProQual: Level 6 (10 units)
        template, created = ProgramTemplate.objects.get_or_create(
            provider=proqual,
            field=fields['proqual_ohs'],
            level=levels[6],
            defaults={
                'name': 'ProQual Level 6',
                'duration_weeks': 32,  # 8 months
                'default_unit_count': 10,
                'has_forms_phase': True,
                'forms_weeks': 8,
            }
        )
        if created:
            self._create_proqual_units(template, 10)
            self.stdout.write(self.style.SUCCESS(f'  Created: {template}'))

        # ProQual: Level 7 (5 units)
        template, created = ProgramTemplate.objects.get_or_create(
            provider=proqual,
            field=fields['proqual_ohs'],
            level=levels[7],
            defaults={
                'name': 'ProQual Level 7',
                'duration_weeks': 32,  # 8 months
                'default_unit_count': 5,
                'has_forms_phase': True,
                'forms_weeks': 8,
            }
        )
        if created:
            self._create_proqual_units(template, 5)
            self.stdout.write(self.style.SUCCESS(f'  Created: {template}'))

        self.stdout.write(self.style.SUCCESS('\nSeeding completed successfully!'))
        self.stdout.write(f'\nTotal Program Templates: {ProgramTemplate.objects.count()}')
        self.stdout.write(f'Total Unit Templates: {UnitTemplate.objects.count()}')

    def _create_othm_units(self, template, unit_count):
        """Create unit templates for OTHM programs"""
        # OTHM: Units are spread evenly across the duration
        weeks_per_unit = max(1, template.duration_weeks // unit_count)
        
        for i in range(1, unit_count + 1):
            UnitTemplate.objects.get_or_create(
                program=template,
                order=i,
                defaults={
                    'title': f'Unit {i}',
                    'offset_weeks': (i - 1) * weeks_per_unit + 1,
                }
            )

    def _create_proqual_units(self, template, unit_count):
        """Create unit templates for ProQual programs"""
        # ProQual: 8 weeks for forms, then units start
        forms_weeks = template.forms_weeks or 8
        remaining_weeks = template.duration_weeks - forms_weeks
        weeks_per_unit = max(1, remaining_weeks // unit_count)
        
        for i in range(1, unit_count + 1):
            UnitTemplate.objects.get_or_create(
                program=template,
                order=i,
                defaults={
                    'title': f'Unit {i}',
                    'offset_weeks': forms_weeks + (i - 1) * weeks_per_unit + 1,
                }
            )

