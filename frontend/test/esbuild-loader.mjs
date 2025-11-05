import { access, readFile } from 'node:fs/promises'
import { constants as fsConstants } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { transform } from 'esbuild'

export async function load(url, context, defaultLoad) {
  if (url.endsWith('.jsx')) {
    const filepath = fileURLToPath(url)
    const source = await readFile(filepath, 'utf8')
    const { code } = await transform(source, {
      loader: 'jsx',
      jsx: 'automatic',
      sourcemap: 'inline',
      format: 'esm',
      define: {
        'import.meta.env.VITE_API_BASE': JSON.stringify(process.env.VITE_API_BASE ?? ''),
        'import.meta.env': '{}',
      },
    })
    return { format: 'module', source: code, shortCircuit: true }
  }

  return defaultLoad(url, context, defaultLoad)
}

export async function resolve(specifier, context, defaultResolve) {
  try {
    return await defaultResolve(specifier, context, defaultResolve)
  } catch (error) {
    if (
      error.code === 'ERR_MODULE_NOT_FOUND' &&
      context.parentURL &&
      (specifier.startsWith('./') || specifier.startsWith('../')) &&
      !specifier.endsWith('.js') &&
      !specifier.endsWith('.jsx') &&
      !specifier.endsWith('.ts') &&
      !specifier.endsWith('.json')
    ) {
      const candidateURL = new URL(`${specifier}.jsx`, context.parentURL)
      try {
        await access(fileURLToPath(candidateURL), fsConstants.F_OK)
        return { url: candidateURL.href, shortCircuit: true }
      } catch {
        // fall through to throw original error
      }
    }

    throw error
  }
}
