const cp = require('child_process')

exports.judge_handler = function(event, context, callback) {
    console.log('=================Run subprocess=================')
    const n = cp.fork('./subprocess.js')
    
    function ret(result){
        n.kill('SIGINT')
        callback(null, result)
    } 
    
    let timeout = setTimeout(()=>{
        ret({
            error: 'TLE'
        })
    }, event.timeout)
    let t = 0
    n.on('message', (m) => {
        if(m == 'READY' && t == 0){
            console.log('=================Subprocess Ready===============');
            t = - process.uptime()
            n.send(event)
        }else{
            t += process.uptime()
            clearTimeout(timeout)
            console.log('=================Get Result=====================');
            console.log(m)
            m.run_duration = Math.round(t * 1000)
            ret(m)
            return
        }
    });
}

///////////////////////////////////////////
//event = {
//    params:[ 
//        { name: 'a', type: 'int', description: 'A' },
//        { name: 'b', type: 'int', description: 'B' }
//    ],
//    timeout: 3000,
//    method: 'aplusb',
//    testcase: [ [ 1, 2 ], [ 2, 2 ] ],
//    code: 'function aplusb(a, b){\n console.log(`${a} + ${b} = ${a+b}`)\n console.error(`${a} + ${b} = ${a+b}`)\n throw \'Guck\'\n return a + b + 1\n}'
//}
//
//
//context = {}
//callback = (err, result) =>{
//    console.log('============@@@@@@@=================')
//    console.log('err', err)
//    console.log('result', result)
//}
//
//exports.judge_handler(event, context, callback)