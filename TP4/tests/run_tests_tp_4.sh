#!/bin/bash

min_percentage_matching_per_test=75  # Establecer el porcentaje mínimo de coincidencia para pasar el test
min_average_percentage_over_all_test=75
min_quantity_test=1
pass_tests=1

total_tests=0
passed_tests=0
total_percentage=0

# Ejecutar pruebas
for input_file in ./TP4/tests/test_*.i; do
    total_tests=$((total_tests + 1))
    test_name=$(basename ${input_file} .i)
    output_file="./TP4/tests/output_${test_name}.txt"
    expected_output="./TP4/tests/expected_outputs/expected_output_${test_name}.txt"

    # Ejecutar el programa con rutas de archivo de entrada y salida
    TP4/bin/tp4 ${input_file} > ${output_file}

    # Normalizar ambos archivos (limpieza de espacios, tabulaciones, etc)
    sed -e 's/\t/ /g' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/[[:space:]]\{2,\}/ /g' -e '/^$/d' "$output_file" > "./TP4/tests/output_${test_name}_clean.txt"
    sed -e 's/\t/ /g' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/[[:space:]]\{2,\}/ /g' -e '/^$/d' "$expected_output" > "./TP4/tests/expected_outputs/expected_output_${test_name}_clean.txt"

    # Contar líneas en los archivos limpios
    output_line_count=$(wc -l < "./TP4/tests/output_${test_name}_clean.txt")
    expected_line_count=$(wc -l < "./TP4/tests/expected_outputs/expected_output_${test_name}_clean.txt")

    [ -n "$(tail -c 1 ./TP4/tests/output_${test_name}_clean.txt)" ] && echo "" >> ./TP4/tests/output_${test_name}_clean.txt
    [ -n "$(tail -c 1 ./TP4/tests/expected_outputs/expected_output_${test_name}_clean.txt)" ] && echo "" >> ./TP4/tests/expected_outputs/expected_output_${test_name}_clean.txt

    # Usar diff para encontrar diferencias ignorando líneas vacías y normalizadas
    diff_output=$(diff "./TP4/tests/output_${test_name}_clean.txt" "./TP4/tests/expected_outputs/expected_output_${test_name}_clean.txt" | grep -vE '^[0-9]+[acd][0-9]+$|^---$')

    # Contar las líneas coincidentes del output de la ejecución respecto del esperado
    matching_lines=$((expected_line_count - $(echo "$diff_output" | grep -c '^>')))

    # Calcular porcentaje de coincidencia
    if [ "$expected_line_count" -gt 0 ] && [ "$output_line_count" -gt 0 ]; then
        percentage_matching_expected=$(awk "BEGIN {printf \"%.2f\", ($matching_lines / $expected_line_count) * 100}")
        percentage_matching_output=$(awk "BEGIN {printf \"%.2f\", ($matching_lines / $output_line_count) * 100}")
        percentage_matching=$(awk "BEGIN {printf \"%.2f\", ($percentage_matching_expected < $percentage_matching_output ? $percentage_matching_expected : $percentage_matching_output)}")
    else
        percentage_matching=0
    fi

    # Sumarizar para promedio
    total_percentage=$(echo "$total_percentage + $percentage_matching" | bc)

    # Determinar si el test es pasado o no basado en el porcentaje de coincidencia
    if (( $(echo "$percentage_matching >= $min_percentage_matching_per_test" | bc) )); then
        passed_tests=$((passed_tests + 1))
        echo -e "\nResultado ${test_name}:\033[32m PASS con ${percentage_matching}% de cobertura\033[0m"
    else
        echo -e "\nResultado ${test_name}:\033[31m FAIL con ${percentage_matching}% de cobertura. Mínimo a alcanzar para superar test: ${min_percentage_matching_per_test}%\033[0m"
    fi

    echo -e "\nDiferencias indicadas según colores de referencia: \n\033[32m  * Verde: Líneas faltantes en salida actual \033[0m\n\033[31m  * Rojo: Líneas adicionales en salida actual \033[0m\n\033[36m  * Cian: Líneas con diferencias entre salida actual y esperada\033[0m"
    echo -e "\nSalida de ejecución actual ${test_name} \t\t\t\tSalida esperada ${test_name}\n"
    colordiff -y "./TP4/tests/output_${test_name}_clean.txt" "./TP4/tests/expected_outputs/expected_output_${test_name}_clean.txt"

done

# Calcular el porcentaje promedio de coincidencia
if [ "$total_tests" -ne 0 ]; then
    average_percentage=$(echo "scale=2; $total_percentage / $total_tests" | bc)
else
    average_percentage=0
fi

echo -e "\nSe superaron en total ${passed_tests} test de un total de ${total_tests} tests \n"
echo -e "Porcentaje promedio de cobertura de test: ${average_percentage}%"

if (( $(echo "$passed_tests < $min_quantity_test" | bc) )); then
    pass_tests=0
    echo -e "\n\033[31mNo se superó la cantidad mínima de test para revisión de PR. Superar como mínimo ${min_quantity_test} de ${total_tests} \033[0m\n"
    exit 1
fi

if (( $(echo "$average_percentage <= $min_average_percentage_over_all_test" | bc) )); then
    pass_tests=0
    echo -e "\n\033[31mNo se alcanzó el mínimo porcentaje promedio de cobertura de test para revisión de PR. Mínimo de porcentaje promedio de cobertura requerido: ${min_average_percentage_over_all_test}%\033[0m\n"
    exit 1
fi

if [ "$pass_tests" -ne 0 ]; then
    echo -e "\n\033[32mSe superaron los requerimientos de los test, puede continuarse con revisión de PR\033[0m\n"
    exit 0

fi
