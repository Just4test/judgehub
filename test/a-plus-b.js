function aplusb(a, b){
    console.log(`${a} + ${b} = ${a+b}`)
    console.error('Throw new error')
    throw 'Guck'
    return a + b + 1
}