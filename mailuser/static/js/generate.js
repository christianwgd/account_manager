    $(document).ready(function(){
        $('#_gen_username').on('click', function(event) {
            var tenant_id = $('#id_tenant').text();
            console.log(tenant_id);
            if (!tenant_id) {
                alert('Kein Mandant vorhanden!');
                return;
            }
            var firstname = $('#id_first_name').val().toLowerCase();
            if (!firstname) {
                alert('Vorname nicht eingegeben!');
                return;
            }
            var lastname = $('#id_last_name').val().toLowerCase();
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
        });
        $('#_gen_password').on('click', function(event) {
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
        });
    });