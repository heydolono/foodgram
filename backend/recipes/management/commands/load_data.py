import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузить данные из CSV-файла'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        with open(options['filename'], 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                ingredient = Ingredient()
                ingredient.name = row[0]
                ingredient.measurement_unit = row[1]
                ingredient.save()