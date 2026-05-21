import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from .models import Nodo


def tree_view(request):
    return render(request, 'soporte/tree.html')


def api_nodos(request):
    nodos = Nodo.objects.all()
    data = [n.to_dict() for n in nodos]
    return JsonResponse({'data': data})


def api_nodo_detail(request, nodo_id):
    nodo = get_object_or_404(Nodo, id=nodo_id)
    data = nodo.to_dict(include_children=True)
    return JsonResponse({'data': data})


def api_nodo_children(request, nodo_id):
    nodo = get_object_or_404(Nodo, id=nodo_id)
    children = nodo.children.all()
    data = [c.to_dict() for c in children]
    return JsonResponse({'data': data})


def api_raices(request):
    raices = Nodo.objects.filter(parent__isnull=True)
    data = [r.to_dict(include_children=True) for r in raices]
    return JsonResponse({'data': data})


def api_tree_full(request):
    raices = Nodo.objects.filter(parent__isnull=True)
    data = [r.to_dict(include_children=True) for r in raices]
    return JsonResponse({'data': data})


@csrf_exempt
def api_nodo_create(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        body = json.loads(request.body)
        nombre = body.get('nombre', '').strip()
        if not nombre:
            return JsonResponse({'error': 'El nombre es obligatorio'}, status=400)
        descripcion = body.get('descripcion', '')
        parent_id = body.get('parent_id')
        orden = body.get('orden', 0)
        parent = None
        if parent_id:
            parent = get_object_or_404(Nodo, id=parent_id)
        nodo = Nodo.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            parent=parent,
            orden=orden
        )
        return JsonResponse({'data': nodo.to_dict()}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)


@csrf_exempt
def api_nodo_update(request, nodo_id):
    nodo = get_object_or_404(Nodo, id=nodo_id)
    if request.method not in ('PUT', 'PATCH'):
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        body = json.loads(request.body)
        if 'nombre' in body:
            nombre = body['nombre'].strip()
            if not nombre:
                return JsonResponse({'error': 'El nombre no puede estar vacío'}, status=400)
            nodo.nombre = nombre
        if 'descripcion' in body:
            nodo.descripcion = body['descripcion']
        if 'parent_id' in body:
            nodo.parent = get_object_or_404(Nodo, id=body['parent_id']) if body['parent_id'] else None
        if 'orden' in body:
            nodo.orden = body['orden']
        nodo.full_clean()
        nodo.save()
        return JsonResponse({'data': nodo.to_dict()})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_nodo_delete(request, nodo_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    nodo = get_object_or_404(Nodo, id=nodo_id)
    nodo.delete()
    return JsonResponse({'message': 'Nodo eliminado correctamente'}, status=200)
