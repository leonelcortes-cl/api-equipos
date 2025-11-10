from django.db import models

class TdEquipos(models.Model):
    idtxt_ppu = models.CharField(db_column='idTxt_Ppu', primary_key=True, max_length=7)
    dttxt_marca = models.CharField(db_column='dtTxt_Marca', max_length=50, blank=True, null=True)
    dttxt_modelo = models.CharField(db_column='dtTxt_Modelo', max_length=50, blank=True, null=True)

    class Meta:
        managed = False  # Django no la crea ni la modifica
        db_table = 'tdEquipos'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'

    def __str__(self):
        return f"{self.idtxt_ppu} - {self.dttxt_marca} {self.dttxt_modelo}"


class TdOperadores(models.Model):
    idnum_rut = models.IntegerField(db_column='idNum_Rut', primary_key=True)
    dttxt_nombre = models.CharField(db_column='dtTxt_Nombre', max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tdOperadores'
        verbose_name = 'Operador'
        verbose_name_plural = 'Operadores'

    def __str__(self):
        return f"{self.dttxt_nombre} ({self.idnum_rut})"


class TdHorometro(models.Model):
    idtxt_ppu = models.ForeignKey(
        TdEquipos,
        db_column='idTxt_Ppu',
        on_delete=models.DO_NOTHING,
        related_name='registros_horometro'
    )
    idnum_rut = models.ForeignKey(
        TdOperadores,
        db_column='idNum_Rut',
        on_delete=models.DO_NOTHING,
        related_name='registros_operador'
    )
    dtnum_horometro = models.IntegerField(db_column='dtNum_Horometro')
    dtfec_registro = models.DateField(db_column='dtFec_Registro')

    class Meta:
        managed = False
        db_table = 'tdHorometro'
        verbose_name = 'Registro de Horómetro'
        verbose_name_plural = 'Registros de Horómetros'

    def __str__(self):
        return f"{self.idtxt_ppu} - {self.idnum_rut} ({self.dtfec_registro})"
