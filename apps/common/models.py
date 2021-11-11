from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True


    def _cria_usuario(self, email, password, **extra_fields):
        """Create and save a User with the given phone and password."""
        if not email:
            raise ValueError('O usuário deve possuir um email válido')
        self.email = email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def cria_cliente(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._cria_usuario(email, password, **extra_fields)

    def cria_funcionario(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', True)
        return self._cria_usuario(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self._cria_usuario(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    """User model."""
    nome = models.CharField(_('nome'), max_length=30, blank=True)
    sobrenome = models.CharField(_('sobrenome'), max_length=150, blank=True)
    telefone = models.CharField(_('telefone'), max_length=11)
    email = models.EmailField(blank=True, null=True, unique=True)
    rg = models.CharField(_('rg'), max_length=12, null=True, blank=True)
    cpf = models.CharField(_('cpf'), max_length=11, null=True, blank=True)
    endereco = models.ManyToManyField('Endereco', through='UsuarioEndereco', through_fields=('idcliente', 'idendereco'), )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']
    
    objects = UserManager()

    def __str__(self):
        return self.nome + ' ' + self.sobrenome

class Endereco(models.Model):
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255, blank=True, null=True)
    cep = models.CharField(max_length=255, blank=True, null=True)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    municipio = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'endereco'

class FormaPagamento(models.Model):
    forma = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'formapagamento'

class Insumo(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255, blank=True, null=True)
    quantidade = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'insumo'

class StatusPedido(models.Model):
    status = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'statuspedido'

class Pedido(models.Model):
    idcliente = models.IntegerField()
    idformapagamento = models.ForeignKey(FormaPagamento, models.DO_NOTHING, db_column='idformapagamento')
    idstatus = models.ForeignKey(StatusPedido, models.DO_NOTHING, db_column='idstatus')
    data = models.DateField()
    obs = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pedido'


class ProdutoTipo(models.Model):
    tipo = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'produtotipo'


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255, blank=True, null=True)
    preco = models.FloatField(blank=True, null=True)
    imagem = models.CharField(max_length=255, blank=True, null=True)
    idtipo = models.ForeignKey(ProdutoTipo, models.DO_NOTHING, db_column='idtipo')
    preco_meio = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'produto'


class ProdutoInsumo(models.Model):
    idproduto = models.ForeignKey(Produto, models.DO_NOTHING, db_column='idproduto')
    idinsumo = models.ForeignKey(Insumo, models.DO_NOTHING, db_column='idinsumo')

    class Meta:
        managed = False
        db_table = 'produtoinsumo'


class ProdutoPedido(models.Model):
    idproduto = models.ForeignKey(Produto, models.DO_NOTHING, db_column='idproduto')
    idpedido = models.ForeignKey(Pedido, models.DO_NOTHING, db_column='idpedido')
    preco = models.FloatField()
    quantidade = models.FloatField()

    class Meta:
        managed = False
        db_table = 'produtopedido'


class UsuarioEndereco(models.Model):
    idcliente = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='idcliente')
    idendereco = models.ForeignKey(Endereco, models.CASCADE, db_column='idendereco')
    primario = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarioendereco'