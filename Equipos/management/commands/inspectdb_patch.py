from django.core.management.commands.inspectdb import Command as InspectDBCommand

class Command(InspectDBCommand):
    def handle_inspection(self, options):
        """
        Sobrescribe la función original de inspectdb para evitar el uso
        de row.comment, que no existe en mysql.connector.
        """
        try:
            for line in super().handle_inspection(options):
                yield line
        except AttributeError as e:
            if "'FieldInfo' object has no attribute 'comment'" in str(e):
                # Ignora los comentarios y sigue
                print("Comentarios ignorados (mysql.connector no los soporta)")
            else:
                raise