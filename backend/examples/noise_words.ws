define Component NoiseTest {
    # 'create' and 'make' are noise words and should be skipped
    create Int x = 10
    make String y = "hello"
    
    # Only identifiers 'x' and 'y' (and types) should appear
    # 'create' and 'make' will disappear from the token stream
}
