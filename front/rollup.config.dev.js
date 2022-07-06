import nodeResolve from 'rollup-plugin-node-resolve'
import copy from 'rollup-plugin-copy'
import browsersync from 'rollup-plugin-browsersync'
import { terser } from 'rollup-plugin-terser'

export default {
  input: 'index.js',
  output: {
    file: 'dist/bundle.js',
    format: 'es',
    sourcemap: true
  },
  plugins: [
    nodeResolve({
      browser: true
    }),
    copy({
      targets: [
        { src: './index.html', dest: './dist'},
        { src: './favicon.ico', dest: './dist'},
        { src: './node_modules/@kor-ui/kor/kor-styles.css', dest: './dist' },
        { src: './node_modules/@kor-ui/kor/fonts', dest: './dist'}
      ]
    }),
    browsersync({
      server: 'dist',
      open: false,
      watch: true,
      port: 80
    }),
    terser({ module: true })
  ]
}