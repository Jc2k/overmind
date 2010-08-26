from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from overmind.provisioning.models import Provider, Instance
from overmind.provisioning.forms import ProviderForm, InstanceForm
from overmind.provisioning.controllers import ProviderController
from libcloud.types import NodeState, InvalidCredsException


def overview(request):
    provider_list = Provider.objects.all()
    instance_list = Instance.objects.all()
    return render_to_response('overview.html', {
        'instance_list': instance_list,
        'provider_list': provider_list,
    })

def newprovider(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ProviderForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Check that the account is valid
            Prov = form.save(commit = False)
            try:
                controller = ProviderController(Prov)
                form.save()
                return HttpResponseRedirect('/overview/') # Redirect after POST
            except InvalidCredsException:
                pass
                #TODO: return a form error
                #TODO: rackspace returns InvalidCredsException on class init but EC2 does not
    else:
        form = ProviderForm() # An unbound form

    return render_to_response('provider.html', { 'form': form })

def deleteprovider(request, provider_id):
    #TODO: Introduce checks
    #TODO: turn into DELETE request? completely RESTify?
    provider = Provider.objects.get(id=provider_id)
    provider.delete()
    return HttpResponseRedirect('/overview/')

def newnode(request):
    if request.method == 'POST':
        form = InstanceForm(request.POST)
        if form.is_valid():
            Inst = form.save(commit = False)
            controller = ProviderController(Inst.provider)
            data_from_provider = controller.spawn_new_instance(form)
            if data_from_provider is not None:
                #TODO: do extra things with data_from_provider
                Inst.save()
                return HttpResponseRedirect('/overview/')
    else:
        form = InstanceForm()
    
    return render_to_response('node.html', { 'form': form })

def deletenode(request, node_id):
    #TODO: turn into DELETE request? completely RESTify?
    #TODO: introduce checks
    #TODO: call ProviderController.delete()
    node = Instance.objects.get(id=node_id)
    node.delete()
    return HttpResponseRedirect('/overview/')
