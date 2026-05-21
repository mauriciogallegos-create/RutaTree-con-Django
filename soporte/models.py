from django.db import models


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

    def __str__(self):
        return self.nombre

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

    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'parent_id': self.parent_id,
            'orden': self.orden,
            'depth': self.get_depth(),
            'is_leaf': self.is_leaf(),
        }
        if include_children:
            data['hijos'] = [
                child.to_dict(include_children=True)
                for child in self.children.all()
            ]
        return data
