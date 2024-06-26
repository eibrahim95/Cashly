# Generated by Django 4.2.11 on 2024-04-30 20:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_cashcollector_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerBill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=4, max_digits=20)),
                ('due_date', models.DateField()),
                ('collector', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assigned_bills', to='users.cashcollector')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_bills', to='users.manager')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bills', to='billing.customer')),
            ],
        ),
    ]
