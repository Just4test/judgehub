const {NodeVM, VMScript} = require('vm2')
const {Writable} = require('stream')

function run(testcase, methodName, code){
	//capture stdout and stderr
	let stdout = []
	const stdoutStream = new Writable()
	stdoutStream.write = (chunk, encoding, cb) => {stdout.push(chunk)}
	let stderr = []
	const stderrStream = new Writable()
	stderrStream.write = (chunk, encoding, cb) => {stderr.push(chunk)}
	const logger = new console.Console(stdoutStream, stderrStream);
	
	const vm = new NodeVM({
		wrapper:'none',
		sandbox:{
			console:logger
		},
		require:{
			mock:{
				fs: null
			}
		}
	})
	
	var case_p = -1
	let results = []
	try {
		const script = new VMScript(code + '\nreturn ' + methodName);
		method = vm.run(script)
		console.log(method);
		for(c of testcase){
			stdout = []
			stderr = []
			case_p += 1
			let output = method.apply(null, c)
			results.push({
				output: output,
				stdout: stdout.join(''),
				stderr: stderr.join('')
			})
		}
	} catch (err) {
		console.log(err)
		return {
			error: err,
			case_p: case_p,
			stdout: stdout,
			stderr: stderr
		}
	}
	return {
		results: results
	}
}

////////////////////////////////

process.send('READY');

//event = { params:
//	[ { name: 'a', type: 'int', description: 'A' },
//	{ name: 'b', type: 'int', description: 'B' } ],
//	method: 'aplusb',
//	testcase: [ [ 1, 2 ], [ 2, 2 ] ],
//	code: 'function aplusb(a, b){console.log(arguments)\n return a + b\n}' }
var c = 0
process.on('message', (m) => {
	console.log('sub process get message!!!!!', m)
	c += 1
	process.send(run(m.testcase, m.method, m.code))
	//let main process to kill this process
});