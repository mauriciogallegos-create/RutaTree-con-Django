import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db.models import Q
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


def api_nodo_ancestors(request, nodo_id):
    nodo = get_object_or_404(Nodo, id=nodo_id)
    ancestors = nodo.get_ancestors()
    data = [a.to_dict() for a in ancestors]
    return JsonResponse({'data': data, 'path': nodo.get_path_string()})


def api_raices(request):
    raices = Nodo.objects.filter(parent__isnull=True)
    data = [r.to_dict(include_children=True) for r in raices]
    return JsonResponse({'data': data})


def api_tree_full(request):
    raices = Nodo.objects.filter(parent__isnull=True)
    data = [r.to_dict(include_children=True) for r in raices]
    return JsonResponse({'data': data})


def api_tree_stats(request):
    raices = Nodo.objects.filter(parent__isnull=True)
    total = Nodo.objects.count()
    leafs = Nodo.objects.filter(children__isnull=True).distinct().count()
    max_depth = 0
    for nodo in Nodo.objects.all():
        d = nodo.get_depth()
        if d > max_depth:
            max_depth = d
    return JsonResponse({
        'data': {
            'total_nodos': total,
            'nodos_raiz': raices.count(),
            'nodos_hoja': leafs,
            'altura': max_depth + 1 if total > 0 else 0,
            'nodos_internos': total - leafs,
        }
    })


def api_nodo_search(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'data': []})
    nodos = Nodo.objects.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    data = [n.to_dict() for n in nodos]
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
        if len(nombre) > 200:
            return JsonResponse({'error': 'El nombre no puede exceder 200 caracteres'}, status=400)
        descripcion = body.get('descripcion', '')
        parent_id = body.get('parent_id')
        orden = body.get('orden', 0)
        parent = None
        if parent_id:
            parent = get_object_or_404(Nodo, id=parent_id)
        nodo = Nodo(
            nombre=nombre,
            descripcion=descripcion,
            parent=parent,
            orden=orden
        )
        nodo.save()
        return JsonResponse({'data': nodo.to_dict()}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)


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
            if len(nombre) > 200:
                return JsonResponse({'error': 'El nombre no puede exceder 200 caracteres'}, status=400)
            nodo.nombre = nombre
        if 'descripcion' in body:
            nodo.descripcion = body['descripcion']
        if 'parent_id' in body:
            if body['parent_id'] is None:
                nodo.parent = None
            else:
                new_parent = get_object_or_404(Nodo, id=body['parent_id'])
                if new_parent.id == nodo.id:
                    return JsonResponse({'error': 'Un nodo no puede ser padre de sí mismo'}, status=400)
                nodo.parent = new_parent
        if 'orden' in body:
            nodo.orden = body['orden']
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


@csrf_exempt
def api_nodo_move(request, nodo_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    nodo = get_object_or_404(Nodo, id=nodo_id)
    try:
        body = json.loads(request.body)
        new_parent_id = body.get('parent_id')
        if new_parent_id is None:
            nodo.parent = None
        else:
            new_parent = get_object_or_404(Nodo, id=new_parent_id)
            if new_parent.id == nodo.id:
                return JsonResponse({'error': 'Un nodo no puede ser padre de sí mismo'}, status=400)
            if nodo.is_ancestor_of(new_parent):
                return JsonResponse({'error': 'Movimiento inválido: causaría una referencia circular'}, status=400)
            nodo.parent = new_parent
        if 'orden' in body:
            nodo.orden = body['orden']
        nodo.save()
        return JsonResponse({'data': nodo.to_dict()})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_seed_data(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    if Nodo.objects.exists():
        return JsonResponse({'error': 'Ya existen datos en el sistema. Elimínelos primero.'}, status=400)

    data = [
        {'nombre': 'Trámites Administrativos', 'descripcion': 'Gestión de trámites institucionales', 'parent_id': None, 'orden': 1},
        {'nombre': 'Matrícula', 'descripcion': 'Procesos de matrícula académica', 'parent_id': None, 'orden': 1},
        {'nombre': 'Certificados', 'descripcion': 'Solicitud y emisión de certificados', 'parent_id': None, 'orden': 2},
        {'nombre': 'Pagos', 'descripcion': 'Gestión de pagos y aranceles', 'parent_id': None, 'orden': 3},
        {'nombre': 'Requisitos', 'descripcion': 'Documentos requeridos para matrícula', 'parent_id': None, 'orden': 1},
        {'nombre': 'Solicitud', 'descripcion': 'Formulario de solicitud de matrícula', 'parent_id': None, 'orden': 2},
        {'nombre': 'Notas', 'descripcion': 'Certificados de notas', 'parent_id': None, 'orden': 1},
        {'nombre': 'Estudio', 'descripcion': 'Certificados de estudio', 'parent_id': None, 'orden': 2},
        {'nombre': 'Egreso', 'descripcion': 'Certificados de egreso', 'parent_id': None, 'orden': 3},
        {'nombre': 'Aranceles', 'descripcion': 'Pago de aranceles universitarios', 'parent_id': None, 'orden': 1},
        {'nombre': 'Multas', 'descripcion': 'Pago de multas y moras', 'parent_id': None, 'orden': 2},
    ]

    created = {}
    for item in data:
        parent = created.get(item['parent_id']) if item.get('parent_id') else None
        nodo = Nodo.objects.create(
            nombre=item['nombre'],
            descripcion=item['descripcion'],
            parent=parent,
            orden=item['orden']
        )
        created[item['nombre']] = nodo

    required_parents = {
        'Requisitos': 'Matrícula',
        'Solicitud': 'Matrícula',
        'Notas': 'Certificados',
        'Estudio': 'Certificados',
        'Egreso': 'Certificados',
        'Aranceles': 'Pagos',
        'Multas': 'Pagos',
    }
    for child_name, parent_name in required_parents.items():
        if child_name in created and parent_name in created:
            created[child_name].parent = created[parent_name]
            created[child_name].save()

    raices = Nodo.objects.filter(parent__isnull=True)
    return JsonResponse({
        'message': 'Datos de ejemplo cargados correctamente',
        'data': [r.to_dict(include_children=True) for r in raices]
    }, status=201)
