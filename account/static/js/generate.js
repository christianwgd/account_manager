function gen_username(tenant_id) {
    if (!$) {
        $ = django.jQuery;
    }

    if (!tenant_id) {
        alert('Kein Mandant vorhanden!');
        return;
    }
    var firstname = normalize($('#id_first_name').val());
    if (!firstname) {
        alert('Vorname nicht eingegeben!');
        return;
    }
    var lastname = normalize($('#id_last_name').val());
    if (!lastname) {
        alert('Nachname nicht eingegeben!');
        return;
    }
    //get tenants domain
    $.ajax({
        type: 'GET',
        url: '/get_tenant_domain/'+tenant_id+'/',
        success: function(domain){
            $('#id_username').val(firstname+'.'+lastname+'@'+domain);
        },
        error: function (xhr, ajaxOptions, thrownError){
            alert(thrownError);
        }
    });
};

function gen_password() {
    if (!$) {
        $ = django.jQuery;
    }
    
    $.ajax({
        type: 'GET',
        url: '/get_default_password/',
        success: function(password){
            $('#id_def_pwd').val(password);
        },
        error: function (xhr, ajaxOptions, thrownError){
            alert(thrownError);
        }
    });
};