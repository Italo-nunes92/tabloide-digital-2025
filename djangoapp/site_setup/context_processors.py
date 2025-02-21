from site_setup.models import SiteSetup
from tabloide.models import Store

def example(request):
    return {
        'example': 'veio o context processor'
    }

def site_setup(request):
    setup = SiteSetup.objects.order_by('-id').first()
    return {
        'site_setup':setup   
        
    }
    
def store_selection(request):
    stores = Store.objects.all()
    
    return {
        'stores_test': stores
    }