from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.http import HttpResponse, Http404
from django.contrib.messages import constants
from django.contrib import messages
# Create your views here.

def novo_flashcard(request):
    if not request.user.is_authenticated: # Verifica se o usuário está logado em alguma conta, se não ele manda para página de logar.
        return redirect('/usuarios/logar')
    
    if request.method == "GET":
        categorias = Categoria.objects.all() # Puxa as categorias do banco de dados
        dificuldades = Flashcard.DIFICULDADE_CHOICES # Flashcard está dentro de models.py, que representa o banco de dados
        flashcards = Flashcard.objects.filter(user=request.user)

        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get("dificuldade")

        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id=categoria_filtrar) 

        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtrar)

        return render(request, 'novo_flashcard.html', {'categorias': categorias, 
                                                       'dificuldades': dificuldades,
                                                       'flashcards': flashcards}) # Envia os dados de Categorias para o Front-End através da tag de print do Django {{ }}
    elif request.method == "POST":
        pergunta = request.POST.get('pergunta') # Caso o usuário aperte para criar um novo flashcard, aqui ele vai receber os itens que ele colocou.
        resposta = request.POST.get('resposta') # Cada um busca com o name dado no html e no banco de dados.
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0: 
            # Não deixa ele cadastrar
            messages.add_message(request, constants.ERROR, "Preenchas os campos de pergunta e resposta")
            return redirect('/flashcard/novo_flashcard')
        
        
        
        flashcard = Flashcard(
            user=request.user,
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria, # Recebe apenas a ID
            dificuldade=dificuldade,
        )

        flashcard.save() # .save vai salvar os dados no banco 

        messages.add_message(request, constants.SUCCESS, "Flashcard criado com sucesso")

        return redirect('/flashcard/novo_flashcard')

def deletar_flashcard(request, id):

    flashcard = Flashcard.objects.get(id=id)

    if not flashcard.user == request.user:
        messages.add_message(request, constants.ERROR, "Erro tente, novamente")
        return redirect('/flashcard/novo_flashcard')
    
    messages.add_message(
        request, constants.SUCCESS, 'Flashcard deletado com sucesso!'
    )
    return redirect('/flashcard/novo_flashcard/')

def iniciar_desafio(request):

    if request.method == "GET":
        categorias = Categoria.objects.all() # Puxa as categorias do banco de dados
        dificuldades = Flashcard.DIFICULDADE_CHOICES # Flashcard está dentro de models.py, que representa o banco de dados
        return render(request, 'iniciar_desafio.html', {'categorias': categorias, 'dificuldades': dificuldades})
    elif request.method == "POST":
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        desafio = Desafio(
            user=request.user,
            titulo=titulo,
            quantidade_perguntas=qtd_perguntas,
            dificuldade=dificuldade
        )

        desafio.save()

        for categoria in categorias:
            desafio.categoria.add(categoria)

        flashcards = (
            Flashcard.objects.filter(user=request.user)
            .filter(dificuldade=dificuldade)
            .filter(categoria_id__in=categorias)
            .order_by('?')
        )

        if flashcards.count() < int(qtd_perguntas):
            messages.add_message(request, constants.ERROR, "Você não tem essa quantidade de flashcards")
            return redirect('/flashcard/iniciar_desafio')


        print(flashcards.count())

        flashcards = flashcards[: int(qtd_perguntas)]

        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=f,
            )
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)
        
        desafio.save()

        return redirect('/flashcard/listar_desafio')

def listar_desafio(request):
    
    desafios = Desafio.objects.filter(user=request.user)
    # Desenvolver os status.

    

    # Desenvolver os filtros.
    categorias = Categoria.objects.all() # Puxa as categorias do banco de dados
    dificuldades = Flashcard.DIFICULDADE_CHOICES # Flashcard está dentro de models.py, que representa o banco de dados

    dificuldade_filtrar = request.GET.get('dificuldade.id')
    categoria_filtrar = request.GET.get('categoria.id')

    if dificuldade_filtrar:
        desafios = desafios.filter(dificuldade=dificuldade_filtrar)

    if categoria_filtrar:
        desafios = desafios.filter(categorias__id=categoria_filtrar)

    return render(request, 'listar_desafio.html', {'categorias':categorias, 
                                                   'dificuldades': dificuldades,
                                                   'desafios': desafios, })

def desafio(request, id):
    desafio = Desafio.objects.get(id=id)

    if not desafio.user == request.user:
        raise Http404

    if request.method == "GET":
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
        erros = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()
        faltantes = desafio.flashcards.filter(respondido=False).count()
        return render(request, 'desafio.html', {'desafio':desafio, 'acertos': acertos,
                                                'erros': erros, 'faltantes': faltantes})
    return HttpResponse(id)

def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')

    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404

    flashcard_desafio.respondido = True

    flashcard_desafio.acertou = True if acertou == "1" else False
    flashcard_desafio.save()

    return redirect(f'/flashcard/desafio/{desafio_id}')

def relatorio(request, id):
    desafio = Desafio.objects.get(id=id)

    acertos = desafio.flashcards.filter(acertou=True).count()
    erros = desafio.flashcards.filter(acertou=False).count()

    acertos_e_Erros = [acertos, erros]

    categorias = desafio.categoria.all()
    name_categoria = [i.nome for i in categorias ]

    acertosGr2 = []
    for categoria in categorias:
        acertosGr2.append(desafio.flashcards.filter(flashcard__categoria=categoria).filter(acertou=True).count())

    # Fazer uma parte para melhores e piores matérias ranking

    return render(request, 'relatorio.html', {'desafio':desafio, 
                                              'acertos_e_Erros':acertos_e_Erros, 
                                              'acertosGr2':acertosGr2, 
                                              'categorias':name_categoria})
