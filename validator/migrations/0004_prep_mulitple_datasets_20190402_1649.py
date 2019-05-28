from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0003_celery_task_20190402_1445'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatasetConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dataset_configurations', to='validator.Dataset')),
                ('filters', models.ManyToManyField(related_name='dataset_configurations', to='validator.DataFilter')),
            ],
        ),
        migrations.AddField(
            model_name='datasetconfiguration',
            name='validation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dataset_configurations', to='validator.ValidationRun'),
        ),
        migrations.AddField(
            model_name='datasetconfiguration',
            name='variable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dataset_configurations', to='validator.DataVariable'),
        ),
        migrations.AddField(
            model_name='datasetconfiguration',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dataset_configurations', to='validator.DatasetVersion'),
        ),
        migrations.RenameField(
            model_name='validationrun',
            old_name='scaling_ref',
            new_name='old_scaling_ref'
            ),
        migrations.AddField(
            model_name='validationrun',
            name='scaling_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scaling_ref_validation_run', to='validator.DatasetConfiguration'),
        ),
        migrations.AddField(
            model_name='validationrun',
            name='reference_configuration',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ref_validation_run', to='validator.DatasetConfiguration'),
        ),
    ]
