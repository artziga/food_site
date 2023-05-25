var ingredientCount = {{ formset.total_form_count }};

function updateFormset() {
    $('#id_form-TOTAL_FORMS').val(ingredientCount);
    $('#ingredient-block').append(`{{ formset.empty_form|safe }}`.replace(/__prefix__/g, ingredientCount));
    ingredientCount++;
}

$('#add-ingredient').on('click', function() {
    updateFormset();
});
