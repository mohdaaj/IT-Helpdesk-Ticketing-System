from django.shortcuts import render, get_object_or_404, redirect
from .models import Ticket, Comment
from .forms import TicketForm, CommentForm
from django.contrib.auth.decorators import login_required

# ----------------------
# Ticket Views
# ----------------------

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
    # Only staff can create tickets
    if not hasattr(request.user, 'role') or request.user.role != 'staff':
        return redirect('tickets:ticket_list')
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
    ticket = get_object_or_404(Ticket, pk=pk)
    # Only staff who created the ticket can edit
    if request.user.role == 'staff' and ticket.created_by == request.user:
        if request.method == 'POST':
            form = TicketForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                return redirect('tickets:ticket_detail', pk=ticket.pk)
        else:
            form = TicketForm(instance=ticket)
        return render(request, 'tickets/ticket_form.html', {'form': form})
    # Only helpers can close/justify
    elif request.user.role == 'helper':
        if request.method == 'POST':
            justification = request.POST.get('justification')
            ticket.justification = justification
            ticket.status = 'closed'
            ticket.save()
            # Notification logic will be added later
            return redirect('tickets:ticket_detail', pk=ticket.pk)
        return render(request, 'tickets/ticket_justify.html', {'ticket': ticket})
    else:
        return redirect('tickets:ticket_list')

@login_required
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    # Only staff who created the ticket can delete
    if request.user.role == 'staff' and ticket.created_by == request.user:
        if request.method == 'POST':
            ticket.delete()
            return redirect('tickets:ticket_list')
        return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})
    else:
        return redirect('tickets:ticket_list')

# ----------------------
# Comment Views
# ----------------------

@login_required
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('tickets:ticket_detail', pk=comment.ticket.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'tickets/comment_form.html', {'form': form, 'ticket': comment.ticket})

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    ticket = comment.ticket
    if request.method == 'POST':
        comment.delete()
        return redirect('tickets:ticket_detail', pk=ticket.pk)
    return render(request, 'tickets/comment_confirm_delete.html', {'comment': comment})

# ----------------------
# Pages & Auth Views
# ----------------------
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

def home(request):
    """Login page"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('tickets:ticket_list')
    else:
        form = AuthenticationForm()
    return render(request, 'home.html', {'form': form})

def signup(request):
    """User registration"""
    error_message = ''
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tickets:ticket_list')
        else:
            error_message = 'Invalid sign up – try again.'
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form, 'error_message': error_message})

def about(request):
    return render(request, 'about.html')
