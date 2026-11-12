from bakery import assert_equal
from drafter import *
from dataclasses import dataclass



hide_debug_information()
set_website_title("Stoichiometric Calculator")
set_website_framed(False)



# global constants for mass calculations
ATOMIC_MASSES = {
    "H": 1.008,
    "He": 4.003,
    "Li": 6.94,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "Na": 22.990,
    "Mg": 24.305,
    "S": 32.06,
    "Cl": 35.45,
    "K": 39.098,
    "Ca": 40.078,
}

'''ADVANCED CODING TECHNIQUES FROM CHATGPT
Sets: ChatGPT used sets as a solution to balance chemical equations. The following explanation is my
understanding of what a set is based on my research using non-AI sources:
    Explanation: A set can store multiple items in one variable. They do not have a defined order
    and thus cannot be referred to by an index or a key. They also do not allow duplicate values
    The reason sets are so perfect for the is_balanced function because it inherently prevents
    the program from checking the same element twice.
    
Other, smaller uses of advanced coding techniques are explained in 1 or 2 single line comments
above where the technique was used.
'''

@dataclass
class Molecule:
    atomic_mass: float
    found_mass: float
    found_moles: float
    symbol: str


@dataclass
class State:
    equation: list[Molecule]
    coefficients: list[int]
    moles: bool
    mass: bool


def parse_formula(formula: str) -> dict[str, int]:
    """Convert a chemical formula into a dictionary of element symbols
and their corresponding atom counts.

Args:
    formula: A chemical formula represented as a string.

Returns:
    A dictionary containing each element and its number of atoms.
    """
    elements: dict[str,int] = {}
    i = 0

    while i < len(formula):
        if formula[i].isupper():
            symbol = formula[i]
            i += 1

            if i < len(formula) and formula[i].islower():
                symbol += formula[i]
                i += 1

            number = ""

            while i < len(formula) and formula[i].isdigit():
                number += formula[i]
                i += 1

            if number == "":
                number = "1"

            elements[symbol] = elements.get(symbol, 0) + int(number)

    return elements

assert_equal(parse_formula("H2O"), {"H": 2, "O": 1})
assert_equal(parse_formula("C6H12O6"), {"C": 6, "H": 12, "O": 6})
assert_equal(parse_formula("CH3CH2OH"), {"C": 2, "H": 6, "O": 1})

def is_balanced(formulas: list[dict[str, int]], coefficients: list[int], elements: set[str]) -> bool:
    """Determine whether a chemical equation is balanced.

Checks through each element and makes sure there is the same amount of that element
on either side. 

Args:
    formulas: A list of dictionaries containing element counts
        for each molecule.
    coefficients: A list of coefficients corresponding to each molecule.
    elements: A set of all unique elements in the equation.

Returns:
    True if the number of each type of atom is equal on both sides
    of the equation, otherwise False.
    """

    for element in elements:
        reactants = 0
        products = 0


        #the .get method with the safe return value 0 safely lets the program
        #check to see if there is an element in a molecule. if there isn't, it will
        #return 0. Otherwise, it will add to the reactants/products the number
        #of that element in that instance.
        for i in range(2):
            reactants += formulas[i].get(element, 0) * coefficients[i]

        for i in range(2, len(formulas)):
            products += formulas[i].get(element, 0) * coefficients[i]

        if reactants != products:
            return False

    return True

assert_equal(is_balanced([{"H": 2}, {"O": 2}, {"H": 2, "O": 1}], [2, 1, 2], {"H", "O"}), True)
assert_equal(is_balanced([{"H": 2}, {"O": 2}, {"H": 2, "O": 1}], [1, 1, 1], {"H", "O"}), False)

#the asterisk means that the function can take in a variable number of terms
#this is how the function can deal with having 1 or 2 products
def balance_stoichiometry(*molecules: str) -> list[int]:
    """Find coefficients that balance a chemical equation.

Args:
    *molecules: Chemical formulas represented as individual strings.

Returns:
    A list of integer coefficients that balance the equation.
    Returns an empty list if no solution is found within the
    coefficient search limits.
    """
    
    #this is called dictionary comprehension.
    #python can create a list based on a for loop in one line
    formulas = [parse_formula(molecule) for molecule in molecules]

    elements = set()
    for formula in formulas:
        for element in formula:
            elements.add(element)

    for a in range(1, 30):
        for b in range(1, 30):
            for c in range(1, 30):
                if len(molecules) == 3:
                    coefficients = [a, b, c]
                else:
                    for d in range(1, 30):
                        coefficients = [a, b, c, d]

                        if is_balanced(formulas, coefficients, elements):
                            return coefficients
                    continue

                if is_balanced(formulas, coefficients, elements):
                    return coefficients

    return []

assert_equal(balance_stoichiometry("H2", "O2", "H2O"), [2, 1, 2])
assert_equal(balance_stoichiometry("N2", "H2", "NH3"), [1, 3, 2])
assert_equal(balance_stoichiometry("Fe", "O2", "Fe2O3"), [4, 3, 2])

def calculate_molar_mass(formula: str) -> float:
    """Calculate the molar mass of a chemical formula.

Args:
    formula: A chemical formula represented as a string.

Returns:
    The total molar mass of the molecule in grams per mole.
    """
    elements = parse_formula(formula)
    total_mass = 0.0

    for element in elements:
        total_mass += ATOMIC_MASSES[element] * elements[element]

    return total_mass


def create_molecule(formula: str) -> Molecule:
    """Create a Molecule instance containing its calculated molar mass.

Args:
    formula: The chemical formula of the molecule.

Returns:
    A Molecule object containing the molar mass, initialized
    found mass, initialized found moles, and chemical formula.
    """
    return Molecule(
        calculate_molar_mass(formula),
        0.0,
        0.0,
        formula
    )

assert_equal(calculate_molar_mass("H2O"), 18.015)
assert_equal(calculate_molar_mass("CO2"), 44.009)
assert_equal(create_molecule("H2O"), Molecule(18.015, 0.0, 0.0, "H2O"))

@route
def index(state: State) -> Page:
    """Display the homepage of the chemistry calculator.

Args:
    state: The current application state containing the equation
        and calculation settings.

Returns:
    A Page containing input fields for a chemical equation
    and a molecule investigation, along with navigation buttons.
    """
    return Page(state, [
        Header("Enter your unbalanced reaction: "),
        TextBox("reactant_1", state.equation[0].symbol),
        "+",
        TextBox("reactant_2", state.equation[1].symbol),
        "-->",
        TextBox("product_1", state.equation[2].symbol),
        "+",
        TextBox("product_2", state.equation[3].symbol),
        "\n",
        Button("Balance my Equation!", "balance_equation"),
        Header("Or investigate a molecule: "),
        TextBox("investigate_target",''),
        Button("Investigate Molecule","investigate_molecule")
    ])

@route
def investigate_molecule(state: State, investigate_target: str) -> Page:
    """Calculate and display the molar mass and elemental composition
of a user-provided chemical formula.

Args:
    state: The current application state.
    investigate_target: The chemical formula entered by the user.

Returns:
    A Page displaying the chemical formula, molar mass,
    and percentage by mass of each element.
    """
    elements = parse_formula(investigate_target)
    targetweight = calculate_molar_mass(investigate_target)
    
    percentages = {}
    for element in elements:
        element_mass = ATOMIC_MASSES[element] * elements[element]
        percentages[element] = (element_mass / targetweight) * 100

    
    return Page(state, [
        Header("Chemical Formula: "),
        investigate_target,
        Header("Molecular Weight: "),
        targetweight,
        Header("Element Breakdown: "),
        DefinitionList(percentages),
        '\n',
        Button("Go Back",'index')
            ]
                )

@route
def balance_equation(state: State, reactant_1: str, reactant_2: str, product_1: str, product_2: str) -> Page:
    """Create Molecule objects for the entered equation and find
the coefficients needed to balance the reaction.

Args:
    state: The current application state.
    reactant_1: The chemical formula of the first reactant.
    reactant_2: The chemical formula of the second reactant.
    product_1: The chemical formula of the first product.
    product_2: The chemical formula of the optional second product.

Returns:
    A Page displaying the balanced chemical equation, calculation
    options, and input fields for stoichiometry calculations.
    """

    state.equation = [
        create_molecule(reactant_1),
        create_molecule(reactant_2),
        create_molecule(product_1)
    ]

    if product_2:
        state.equation.append(create_molecule(product_2))

    #as stated before, this is a mixture of list comprehension and
    #the use of asterisk to mark variable numbers of inputs
    state.coefficients = balance_stoichiometry(
        *[molecule.symbol for molecule in state.equation]
    )

    if len(state.equation) == 3:
        return Page(state, [
            Header("Balanced Equation: "),
            str(state.coefficients[0]) + state.equation[0].symbol, '+',
            str(state.coefficients[1]) + state.equation[1].symbol, '-->',
            str(state.coefficients[2]) + state.equation[2].symbol,
            "\n",
            CheckBox("moles_check", state.moles),
            "Moles",
            CheckBox("mass_check", state.mass),
            "Mass (g)",
            "\n",
            SelectBox("chosen_molecule", [
                molecule.symbol for molecule in state.equation
            ]),
            TextBox("given_amount", ""),
            Button("Calculate", "calculate")
        ])

    return Page(state, [
        Header("Balanced Equation: "),
        str(state.coefficients[0]) + state.equation[0].symbol, '+',
        str(state.coefficients[1]) + state.equation[1].symbol, '-->',
        str(state.coefficients[2]) + state.equation[2].symbol, '+',
        str(state.coefficients[3]) + state.equation[3].symbol,
        "\n",
        CheckBox("moles_check", state.moles),
        "Moles",
        CheckBox("mass_check", state.mass),
        "Mass (g)",
        "\n",
        SelectBox("chosen_molecule", [
            molecule.symbol for molecule in state.equation
        ]),
        TextBox("given_amount", ""),
        Button("Calculate", "calculate")
    ])


# ======================== CALCULATE FUNCTION =================================
# I use an ignore comment on the Drafter Tables because Thonny gives me a warning
# about incompatible types, but the Drafter documentation says that I should be fine

@route
def calculate(state: State, chosen_molecule: str, moles_check: bool,
              mass_check: bool, given_amount: str) -> Page:
    """Calculate the theoretical masses and mole amounts of every
molecule in a balanced chemical equation using a given amount
of a selected molecule.

Args:
    state: The current application state containing the equation
        and its balancing coefficients.
    chosen_molecule: The chemical formula selected as the given
        molecule.
    moles_check: Whether the user selected moles as the given unit.
    mass_check: Whether the user selected grams as the given unit.
    given_amount: The numerical amount entered by the user.

Returns:
    A Page displaying the calculated masses and mole amounts
    of each molecule, along with inputs for calculating percent yield.
    """

    chosen = -1
    table = []
    for_select = []
    if len(state.equation) == 3:
        for_select.append(state.equation[2].symbol)
    else:
        for_select.append(state.equation[2].symbol)
        for_select.append(state.equation[3].symbol)

    state.moles = moles_check
    state.mass = mass_check

    for i, molecule in enumerate(state.equation):
        if chosen_molecule == molecule.symbol:
            chosen = i

    if chosen == -1:
        return Page(state, ["error"])

    # error for if both are checked
    if state.mass and state.moles:
        return Page(state, [
            Header("Don't check both boxes"),
            Button("Go Back", "new_calculation")
        ])

    # error for if neither were checked
    elif not state.mass and not state.moles:
        return Page(state, [
            Header("You needed to check a box"),
            Button("Go Back", "new_calculation")
        ])

    # calculation for given moles
    elif state.moles and not state.mass:

        for i, molecule in enumerate(state.equation):
            ratio = state.coefficients[i]/state.coefficients[chosen]
            
            molecule.found_mass = float(given_amount) * ratio * molecule.atomic_mass
            molecule.found_moles = float(given_amount) * ratio

            table.append(molecule)

        return Page(state, [
            Header("Results: "),
            Table(table), # type: ignore[arg-type]
            TextBox("actual_product", ''),
            SelectBox("chosen_product", for_select),
            Button("Calculate Yield", "calculate_yield")
        ])

    # calculation for given mass
    else:
        for i, molecule in enumerate(state.equation):
            ratio = state.coefficients[i]/state.coefficients[chosen]
            
            molecule.found_mass = (float(given_amount)/calculate_molar_mass(state.equation[chosen].symbol)) * ratio * molecule.atomic_mass
            molecule.found_moles = (float(given_amount) / calculate_molar_mass(state.equation[chosen].symbol)) * ratio

            table.append(molecule)

        return Page(state, [
            Header("Results: "),
            Table(table), # type: ignore[arg-type]
            SelectBox("chosen_product", for_select),
            TextBox("actual_product", ''),
            Button("Calculate Yield", "calculate_yield")
        ])


# ======================== END OF CALCULATE FUNCTION ==========================


@route
def calculate_yield(state: State, actual_product: str, chosen_product: str) -> Page:
    """Calculate the percent yield of a chemical reaction using
the actual product amount and theoretical product amount.

Args:
    state: The current application state containing the calculated
        theoretical amounts of each molecule.
    actual_product: The actual amount of product obtained.
    chosen_product: The chemical formula of the product selected
        for the percent yield calculation.

Returns:
    A Page displaying the calculated percent yield and navigation
    options for starting another calculation or restarting the site.
    """

    for molecule in state.equation:
        if chosen_product == molecule.symbol:
            chosen_molecule = molecule
    
    percent_yield = (float(actual_product) / chosen_molecule.found_mass) * 100

    return Page(state, [
        Header("Percent Yield: "),
        percent_yield,
        Button("Restart", 'restart'),
        Button("New Calculation",'new_calculation')
    ])

@route
def new_calculation(state: State) -> Page:
    """Reset the calculation settings and return to the equation
balancing page while keeping the previously entered equation.

Args:
    state: The current application state containing the equation
        and its coefficients.

Returns:
    A Page displaying the equation balancing interface with
    the existing chemical equation.
    """
    state.moles = False
    state.mass = False

    return balance_equation(
        state,
        state.equation[0].symbol,
        state.equation[1].symbol,
        state.equation[2].symbol,
        state.equation[3].symbol if len(state.equation) == 4 else ""
    )

@route
def restart(state: State) -> Page:
    """Reset the application state and return the user to the homepage.

Args:
    state: The current application state.

Returns:
    A Page displaying the homepage with an empty chemical equation
    and reset calculation settings.
    """
    state.equation = state.equation = [
            create_molecule(""),
            create_molecule(""),
            create_molecule(""),
            create_molecule("")
        ]
    state.coefficients = []
    state.moles = False
    state.mass = False

    return index(state)


start_server(
    State(
        equation=[
            create_molecule("H2"),
            create_molecule("O2"),
            create_molecule("H2O"),
            create_molecule("")
        ],
        coefficients=[],
        moles=False,
        mass=False,
    )
)


# ======================== ROUTE UNIT TESTS ========================

# INDEX
test_state = State(
    [create_molecule("H2"), create_molecule("O2"),
     create_molecule("H2O"), create_molecule("")],
    [], False, False
)
assert_equal(isinstance(index(test_state), Page), True)


# INVESTIGATE MOLECULE
test_state = State(
    [create_molecule("H2"), create_molecule("O2"),
     create_molecule("H2O"), create_molecule("")],
    [], False, False
)
assert_equal(isinstance(investigate_molecule(test_state, "H2O"), Page), True)


# BALANCE EQUATION
test_state = State(
    [create_molecule(""), create_molecule(""),
     create_molecule(""), create_molecule("")],
    [], False, False
)
balance_stoichiometry_page = balance_equation(
    test_state, "H2", "O2", "H2O", ""
)
assert_equal(test_state.coefficients, [2, 1, 2])


# CALCULATE
test_state = State(
    [create_molecule("H2"), create_molecule("O2"),
     create_molecule("H2O")],
    [2, 1, 2], True, False
)
calculate_page = calculate(test_state, "H2", True, False, "2")
assert_equal(test_state.equation[2].found_moles, 2.0)


# CALCULATE YIELD
test_state = State(
    [create_molecule("H2"), create_molecule("O2"),
     Molecule(18.015, 36.03, 2.0, "H2O")],
    [2, 1, 2], True, False
)
assert_equal(isinstance(calculate_yield(test_state, "18.015", "H2O"), Page), True)


# NEW CALCULATION
test_state = State(
    [create_molecule("H2"), create_molecule("O2"),
     create_molecule("H2O")],
    [2, 1, 2], True, True
)
new_calculation_page = new_calculation(test_state)
assert_equal((test_state.moles, test_state.mass), (False, False))


# RESTART
test_state = State(
    [create_molecule("H2"), create_molecule("O2"),
     create_molecule("H2O")],
    [2, 1, 2], True, True
)
restart_page = restart(test_state)
assert_equal((test_state.coefficients, test_state.moles, test_state.mass),
             ([], False, False))
