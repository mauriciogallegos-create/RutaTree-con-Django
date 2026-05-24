from django.db import models
from django.core.exceptions import ValidationError


class Nodo(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    orden = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Nodo'
        verbose_name_plural = 'Nodos'

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.parent and self.parent_id == self.id:
            raise ValidationError('Un nodo no puede ser padre de sí mismo')
        if self.parent:
            if self._is_circular(self.parent):
                raise ValidationError('Movimiento inválido: causaría una referencia circular')

    def _is_circular(self, potential_parent):
        if potential_parent.parent is None:
            return False
        if potential_parent.id == self.id:
            return True
        if potential_parent.parent:
            return self._is_circular(potential_parent.parent)
        return False

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_depth(self):
        depth = 0
        node = self.parent
        while node:
            depth += 1
            node = node.parent
        return depth

    def is_leaf(self):
        return not self.children.exists()

    def get_ancestors(self):
        ancestors = []
        node = self.parent
        while node:
            ancestors.append(node)
            node = node.parent
        return list(reversed(ancestors))

    def get_descendants(self):
        result = []
        for child in self.children.all():
            result.append(child)
            result.extend(child.get_descendants())
        return result

    def get_siblings(self):
        if self.parent is None:
            return Nodo.objects.filter(parent__isnull=True).exclude(id=self.id)
        return Nodo.objects.filter(parent=self.parent).exclude(id=self.id)

    def get_path_string(self, separator=' → ', field='nombre'):
        parts = [getattr(self, field)]
        node = self.parent
        while node:
            parts.append(getattr(node, field))
            node = node.parent
        return separator.join(reversed(parts))

    def get_root(self):
        node = self
        while node.parent:
            node = node.parent
        return node

    def count_descendants(self):
        return len(self.get_descendants())

    def is_ancestor_of(self, other):
        if other is None:
            return False
        if other.parent is None:
            return False
        if other.parent.id == self.id:
            return True
        return self.is_ancestor_of(other.parent)

    def has_children(self):
        return self.children.exists()

    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'parent_id': self.parent_id,
            'orden': self.orden,
            'depth': self.get_depth(),
            'is_leaf': self.is_leaf(),
            'has_children': self.has_children(),
            'path': self.get_path_string(),
        }
        if include_children:
            data['hijos'] = [
                child.to_dict(include_children=True)
                for child in self.children.all()
            ]
        return data
