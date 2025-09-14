from django.shortcuts import render, get_object_or_404, redirect
from .models import Ticket, Comment
from .forms import TicketForm, CommentForm
from django.contrib.auth.decorators import login_required

@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(created_by=request.user)
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    comments = ticket.comments.all()
    comment_form = CommentForm()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.ticket = ticket
            new_comment.author = request.user
            new_comment.save()
            return redirect('tickets:ticket_detail', pk=ticket.pk)

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            return redirect('tickets:ticket_list')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_form.html', {'form': form})

@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('tickets:ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'tickets/ticket_form.html', {'form': form})

@login_required
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, created_by=request.user)
    if request.method == 'POST':
        ticket.delete()
        return redirect('tickets:ticket_list')
    return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})
