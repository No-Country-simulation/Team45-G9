# Consumo
Permite calcular que tan eficiente es el usuario comparándolo con el gasto promedio de hogares similares y su perfil de consumo comparándolo con el resto de los hogares de la nación.
| Variable                | Descripción                                                                                                                                                                        | Valores                                                                                    | Tipo     | Ejemplo |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------- | ------- |
| kwh                     | Consumo de electricidad de la vivienda en kilowatt-hora (kWh). Puede informarse de forma anual o mensual; el modelo ofrece mayor precisión cuando se proporciona el consumo anual. | 0–100000.             | numérico | `2000`  |            
| periodo_anual           | Indica si el consumo informado corresponde a un período anual o mensual.                                                                                                           | 1: anual, 0: mensual.                                                                      | numérico | `1`     |

# Cuestionario Base
Permite calcular que tan eficiente es el usuario comparándolo con el gasto promedio de hogares similares y su perfil de consumo comparándolo con el resto de los hogares de la nación.
| Variable                | Descripción                                                                                                                                                                        | Valores                                                                                    | Tipo     | Ejemplo |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------- | ------- |
| pais                    | País donde está ubicada la vivienda, solo para América. Ver tabla debajo                                                                                                                                              | 1-35                                                           | Numérico   |2 |
| estado                  | Estado o provincia donde está ubicada la vivienda. Ver tabla debajo para los códigos de cada país.                                                              | 1-99                                            | Numérico   | 17  |
| dormitorios             | Cantidad de dormitorios, es decir, habitaciones separadas utilizadas para dormir.                                                                                                  | 0: monoambiente/soft, 1–50: cantidad de dormitorios, 999: no sabe/no contesta.          | numérico | `1`     |
| ventanas                | Cantidad de ventanas y puertas balcón de la vivienda.                                                                                                                              | 0: ninguna, 1–99: cantidad, 999: no sabe/no contesta.                                      | numérico | `2`     |
| habitantes_mayores             | Cantidad de habitantes de 18 años o más.                                                                                                |  1–50: cantidad de habitantes, 999: no sabe/no contesta.          | numérico | `1`     |
| habitantes_menores             | Cantidad de habitantes de 17 años o menos.                                                                                                |  0–50: cantidad de habitantes, 999: no sabe/no contesta.          | numérico | `1`     |
| agua_caliente_electrica | Indica si el agua caliente sanitaria (ducha, lavabo y cocina) se calienta mediante electricidad.                                                                                   | 0: no, 1: sí,  999: no sabe/no contesta.                                                                              | numérico | `0`     |
| calefaccion_electrica   | Indica si el sistema principal de calefacción utiliza electricidad.                                                                                                                | 0: no, 1: sí, 999: no sabe/no contesta.                                                                                 | numérico | `0`     |
| secarropas_electrico    | Indica si la vivienda posee un secarropas eléctrico.                                                                                                                                           | 0: no, 1: sí, 999: no sabe/no contesta.                                                                              | numérico | `0`     |
| aire_acondicionado      |  Indica si la vivienda posee aire acondicionado.                                                                                                                   | 0: no, 1: si, 999: no sabe/no contesta. | numérico | `1`     |

# Cuestionario Avanzado
Permite calcular el consumo eléctrico de forma más precisa,  estima el porcentaje de electricidad consumida por el calentador de agua, aire acondicionado, calefacción, cocina, iluminación, refrigeración de alimentos y televisor.

| Variable                | Descripción                                                                                                                                                                        | Valores                                                                                    | Tipo     | Ejemplo |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------- | ------- |
| horno_electrico      |  Indica si la vivienda posee horno electrico.                                                                                                                   | 0: no, 1: si, 999: no sabe/no contesta. | numérico | `1`     |
| agua_caliente_tamano    | Capacidad del tanque del calentador de agua, en galones.                                                                                                                           | 0: no posee, 1–500: capacidad del tanque, 999: no sabe/no contesta.                        | numérico | `30`    |
| flag_galones    | Unidad de la capacidad del tanque del calentador de agua.                                                                                                                           | 1:galones americanos, 2: litros, 3:galones imperiales 999: no sabe/no contesta.                        | numérico | `1`    |
| lavarropas_frecuencia   | Cantidad promedio de ciclos de lavado realizados por semana.                                                                                                                       | 0–50, 999: no sabe/no contesta.                                                            | numérico | `7`     |
| tv_cantidad             | Cantidad de televisores en la vivienda.                                                                                                                                            | 0–50, 999: no sabe/no contesta.                                                            | numérico | `1`     |
| tv_frecuencia          | Cantidad de horas semanales que el televisor principal permanece encendido.                                                                                                                     | 0–168: cantidad de horas, 999: no sabe/no contesta.                                      | numérico | `0`     |
| freezer                 | Cantidad de freezers independientes (separados del refrigerador).                                                                                                                  | 0: ninguno, 1–50: cantidad, 999: no sabe/no contesta.                                      | numérico | `0`     |
| refrigerador            | Cantidad de refrigeradores (heladeras) en la vivienda.                                                                                                                             | 0: ninguno, 1–50: cantidad, 999: no sabe/no contesta.                                      | numérico | `1`     |
| luces_exterior          | Cantidad de lámparas o luces electricas ubicadas en el exterior de la vivienda.                                                                                                                     | 0: ninguna, 1–50: cantidad, 999: no sabe/no contesta.                                      | numérico | `0`     |
| luces_interior_4_horas  | Cantidad de lámparas o luces electricas interiores utilizadas al menos 4 horas por día.                                                                                                     | 0–500, 999: no sabe/no contesta.                                                           | numérico | `3`     |




# Códigos de paises
| Código | País                          |
| ---: | -------------------------------- |
|    1 | CANADA                           |
|    2 | ESTADOS UNIDOS                   |
|    3 | MEXICO                           |
|    4 | BELICE                           |
|    5 | COSTA RICA                       |
|    6 | EL SALVADOR                      |
|    7 | GUATEMALA                        |
|    8 | HONDURAS                         |
|    9 | NICARAGUA                        |
|   10 | PANAMA                           |
|   11 | ANTIGUA AND BARBUDA              |
|   12 | BAHAMAS                          |
|   13 | BARBADOS                         |
|   14 | CUBA                             |
|   15 | DOMINICA                         |
|   16 | REPUBLICA DOMINICANA             |
|   17 | GRENADA                          |
|   18 | HAITI                            |
|   19 | JAMAICA                          |
|   20 | SAINT KITTS AND NEVIS            |
|   21 | SAINT LUCIA                      |
|   22 | SAINT VINCENT AND THE GRENADINES |
|   23 | TRINIDAD AND TOBAGO              |
|   24 | ARGENTINA                        |
|   25 | BOLIVIA                          |
|   26 | BRASIL                           |
|   27 | CHILE                            |
|   28 | COLOMBIA                         |
|   29 | ECUADOR                          |
|   30 | GUYANA                           |
|   31 | PARAGUAY                         |
|   32 | PERU                             |
|   33 | SURINAME                         |
|   34 | URUGUAY                          |
|   35 | VENEZUELA                        |


# Códigos Estados Unidos

| Código | Estado                | Abreviatura |
| -----: | -------------------- | :----------: |
|      1 | Alabama              |      AL      |
|      2 | Alaska               |      AK      |
|      3 | Arizona              |      AZ      |
|      4 | Arkansas             |      AR      |
|      5 | California           |      CA      |
|      6 | Colorado             |      CO      |
|      7 | Connecticut          |      CT      |
|      8 | Delaware             |      DE      |
|      9 | District of Columbia |      DC      |
|     10 | Florida              |      FL      |
|     11 | Georgia              |      GA      |
|     12 | Hawaii               |      HI      |
|     13 | Idaho                |      ID      |
|     14 | Illinois             |      IL      |
|     15 | Indiana              |      IN      |
|     16 | Iowa                 |      IA      |
|     17 | Kansas               |      KS      |
|     18 | Kentucky             |      KY      |
|     19 | Louisiana            |      LA      |
|     20 | Maine                |      ME      |
|     21 | Maryland             |      MD      |
|     22 | Massachusetts        |      MA      |
|     23 | Michigan             |      MI      |
|     24 | Minnesota            |      MN      |
|     25 | Mississippi          |      MS      |
|     26 | Missouri             |      MO      |
|     27 | Montana              |      MT      |
|     28 | Nebraska             |      NE      |
|     29 | Nevada               |      NV      |
|     30 | New Hampshire        |      NH      |
|     31 | New Jersey           |      NJ      |
|     32 | New Mexico           |      NM      |
|     33 | New York             |      NY      |
|     34 | North Carolina       |      NC      |
|     35 | North Dakota         |      ND      |
|     36 | Ohio                 |      OH      |
|     37 | Oklahoma             |      OK      |
|     38 | Oregon               |      OR      |
|     39 | Pennsylvania         |      PA      |
|     40 | Rhode Island         |      RI      |
|     41 | South Carolina       |      SC      |
|     42 | South Dakota         |      SD      |
|     43 | Tennessee            |      TN      |
|     44 | Texas                |      TX      |
|     45 | Utah                 |      UT      |
|     46 | Vermont              |      VT      |
|     47 | Virginia             |      VA      |
|     48 | Washington           |      WA      |
|     49 | West Virginia        |      WV      |
|     50 | Wisconsin            |      WI      |
|     51 | Wyoming              |      WY      |


# Códigos Chile

| Código | Provincia                | Región                               |
| ---: | ----------------------- | ------------------------------------ |
|    1 | ARICA                   | Arica y Parinacota                   |
|    2 | PARINACOTA              | Arica y Parinacota                   |
|    3 | IQUIQUE                 | Tarapacá                             |
|    4 | TAMARUGAL               | Tarapacá                             |
|    5 | ANTOFAGASTA             | Antofagasta                          |
|    6 | EL LOA                  | Antofagasta                          |
|    7 | TOCOPILLA               | Antofagasta                          |
|    8 | COPIAPÓ                 | Atacama                              |
|    9 | CHAÑARAL                | Atacama                              |
|   10 | HUASCO                  | Atacama                              |
|   11 | ELQUI                   | Coquimbo                             |
|   12 | LIMARÍ                  | Coquimbo                             |
|   13 | CHOAPA                  | Coquimbo                             |
|   14 | VALPARAÍSO              | Valparaíso                           |
|   15 | ISLA DE PASCUA          | Valparaíso                           |
|   16 | LOS ANDES               | Valparaíso                           |
|   17 | PETORCA                 | Valparaíso                           |
|   18 | QUILLOTA                | Valparaíso                           |
|   19 | SAN ANTONIO             | Valparaíso                           |
|   20 | SAN FELIPE DE ACONCAGUA | Valparaíso                           |
|   21 | MARGA MARGA             | Valparaíso                           |
|   22 | SANTIAGO                | Metropolitana de Santiago            |
|   23 | CORDILLERA              | Metropolitana de Santiago            |
|   24 | CHACABUCO               | Metropolitana de Santiago            |
|   25 | MAIPO                   | Metropolitana de Santiago            |
|   26 | MELIPILLA               | Metropolitana de Santiago            |
|   27 | TALAGANTE               | Metropolitana de Santiago            |
|   28 | CACHAPOAL               | O'Higgins                            |
|   29 | COLCHAGUA               | O'Higgins                            |
|   30 | CARDENAL CARO           | O'Higgins                            |
|   31 | CURICÓ                  | Maule                                |
|   32 | TALCA                   | Maule                                |
|   33 | LINARES                 | Maule                                |
|   34 | CAUQUENES               | Maule                                |
|   35 | DIGUILLÍN               | Ñuble                                |
|   36 | ITATA                   | Ñuble                                |
|   37 | PUNILLA                 | Ñuble                                |
|   38 | CONCEPCIÓN              | Biobío                               |
|   39 | ARAUCO                  | Biobío                               |
|   40 | BIOBÍO                  | Biobío                               |
|   41 | CAUTÍN                  | La Araucanía                         |
|   42 | MALLECO                 | La Araucanía                         |
|   43 | VALDIVIA                | Los Ríos                             |
|   44 | RANCO                   | Los Ríos                             |
|   45 | LLANQUIHUE              | Los Lagos                            |
|   46 | CHILOÉ                  | Los Lagos                            |
|   47 | OSORNO                  | Los Lagos                            |
|   48 | PALENA                  | Los Lagos                            |
|   49 | COYHAIQUE               | Aysén                                |
|   50 | AYSÉN                   | Aysén                                |
|   51 | GENERAL CARRERA         | Aysén                                |
|   52 | CAPITÁN PRAT            | Aysén                                |
|   53 | MAGALLANES              | Magallanes y de la Antártica Chilena |
|   54 | ÚLTIMA ESPERANZA        | Magallanes y de la Antártica Chilena |
|   55 | TIERRA DEL FUEGO        | Magallanes y de la Antártica Chilena |
|   56 | ANTÁRTICA CHILENA       | Magallanes y de la Antártica Chilena |


