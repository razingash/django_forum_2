from celery import shared_task
from datetime import date, timedelta
from django.db.models import Sum, Case, When, Value, IntegerField
from .models import DailyActivity, UserSpecializations


@shared_task
def test_task():
    return f'every minute check task ___ {DailyActivity.objects.filter(date=date.today())}'

@shared_task
def users_promotion():
    date_to_calculate = date.today() - timedelta(days=1)
    try:
        activities = DailyActivity.objects.filter(date=date_to_calculate).values('user__id', 'activity_spec_id', 'activity_type').annotate(combinations=Sum(Case(When(activity_type='9', then=Value(5)), default=Value(1), output_field=IntegerField(),)))
        exp_for_specs = {spec_id: 0 for spec_id in range(1, 7)}
        for activity in activities:
            exp_for_specs[activity['activity_spec_id']] += activity['combinations']

        for spec_id, experience in exp_for_specs.items():
            exp_for_specs[spec_id] = min(experience, 20)

        specs = UserSpecializations.objects.filter(user_id__in=activities.values_list('user__id', flat=True))
        for spec in specs:
            spec.experience += exp_for_specs[spec.id]
            if spec.experience >= spec.level_of_awareness * 100:
                spec.level_of_awareness += 1
                spec.experience -= spec.level_of_awareness * 100
        UserSpecializations.objects.bulk_update(specs, ['experience', 'level_of_awareness'])
        DailyActivity.objects.filter(date=date_to_calculate).delete()
    except Exception as e:
        return f'CRITICAL ERROR DURING PROMOTIONS: {e}'
    else:
        return 'PROMOTIONS COMPLETED WITHOUT ERRORS'

