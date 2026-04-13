const { spawn, execSync } = require('child_process');
const path = require('path');
const os = require('os');

const isWindows = os.platform() === 'win32';

function killPort(port) {
    try {
        if (isWindows) {
            const output = execSync(`netstat -ano | findstr :${port}`).toString();
            const lines = output.trim().split('\n');
            for (const line of lines) {
                if (line.includes(`:${port}`) && line.includes('LISTENING')) {
                    const parts = line.trim().split(/\s+/);
                    const pid = parts[parts.length - 1];
                    if (pid && pid !== '0') {
                        console.log(`[CLEANUP] Killing process ${pid} on port ${port}...`);
                        execSync(`taskkill /PID ${pid} /F`, { stdio: 'ignore' });
                    }
                }
            }
        } else {
            execSync(`lsof -ti:${port} | xargs kill -9`, { stdio: 'ignore' });
        }
    } catch (e) {
        // Port not in use or error ignoring
    }
}

function runBackend() {
    console.log('[VERSIGHT] Starting Backend...');
    const cmd = isWindows ? 'cmd.exe' : 'sh';
    const args = isWindows ? ['/c', 'run_backend.bat'] : ['./run_backend.sh'];

    const backend = spawn(cmd, args, {
        cwd: __dirname,
        stdio: 'inherit'
    });

    backend.on('error', (err) => console.error('[BACKEND ERROR]', err));
}

function runFrontend() {
    console.log('[VERSIGHT] Starting Frontend...');
    const cmd = isWindows ? 'cmd.exe' : 'sh';
    const args = isWindows ? ['/c', 'run_frontend.bat'] : ['./run_frontend.sh'];

    const frontend = spawn(cmd, args, {
        cwd: __dirname,
        stdio: 'inherit'
    });

    frontend.on('error', (err) => console.error('[FRONTEND ERROR]', err));
}

console.log('==========================================');
console.log('   VERSIGHT AI - UNIFIED START');
console.log('==========================================');

console.log('[CLEANUP] Checking for previous instances...');
killPort(8010);
killPort(5173);
killPort(5174);

runBackend();
runFrontend();

console.log('\nServices are initializing...');
console.log('API: http://127.0.0.1:8010');
console.log('Web: http://localhost:5173');
console.log('==========================================\n');

