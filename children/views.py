from .forms import ChildForm
from django.shortcuts import render, redirect,get_object_or_404
from .models import Child, Documents
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

def submit_child_details(request):
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES, user=request.user)  # Pass the user
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ChildForm()

    return render(request, 'home.html', )


@login_required(login_url='login')
def children_list(request):
    if request.user.is_authenticated:
        children = Child.objects.filter(parent=request.user)
    else:
        children = Child.objects.none()
    return render(request, 'Children/child_view.html', {'children': children})


def child_detail(request, id):
    child = get_object_or_404(Child, id=id)
    documents = Documents.objects.filter(child=id)
    print(len(documents), "+++++++++++++++++++++++")
    context = {
        'child': child,
        "documents":documents
    }
    return render(request, 'Children/child_detail.html',context )


def child_edit(request, id):
    child = get_object_or_404(Child, id=id)
    if request.method == 'POST':
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, 'Child details updated successfully.')
            return redirect('child_detail', id=id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChildForm(instance=child)

    context = {
        'child': child,
        'form': form
    }
    return render(request, 'Children/child_edit.html', context)