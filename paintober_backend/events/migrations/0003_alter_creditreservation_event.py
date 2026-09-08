from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0002_alter_creditreservation_attendee"),
    ]

    operations = [
        migrations.AlterField(
            model_name="creditreservation",
            name="event",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="reservations",
                to="events.event",
            ),
        ),
    ]