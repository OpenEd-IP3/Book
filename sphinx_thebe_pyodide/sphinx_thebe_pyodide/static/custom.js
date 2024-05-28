document.addEventListener("DOMContentLoaded", function() {
    async function main() {
        // Load Pyodide
        let pyodide = await loadPyodide();

        // Load micropip for installing Python packages
        await pyodide.loadPackage("micropip");

        // Install additional packages if needed
        await pyodide.runPythonAsync(`
            import micropip
            await micropip.install("numpy")
            await micropip.install("pandas")
        `);

        window.pyodide = pyodide;

        // Configure Thebe to use Pyodide
        thebelab.bootstrap({
            selector: 'div.highlight',
            kernelOptions: {
                kernelName: 'python',
                path: window.location.pathname
            },
            requestKernel: async function () {
                return {
                    kernelName: 'python',
                    serverSettings: {
                        baseUrl: window.location.origin,
                        wsUrl: window.location.origin.replace(/^http/, 'ws')
                    },
                    kernelType: 'pyodide'
                };
            }
        });
    }

    main();
});

