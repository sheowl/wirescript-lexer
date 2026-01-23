define Component Showcase {
    # Valid operators
    Int a = 10 + 5 * 2
    Int b = (a - 4) / 2
    
    # Relational & Logical
    if (a >= 10 && b != 0) {
        Boolean valid = true || false
    }

    # Compound Assignment
    a += 1
    b -= 2

    # Layout Combinators
    render(hifi | lofi)
    render(Header ^ Footer)
    render(Container >> Component)
}
