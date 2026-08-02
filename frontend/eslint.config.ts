import pluginVue from 'eslint-plugin-vue'
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from '@vue/eslint-config-typescript'
import oxlint from 'eslint-plugin-oxlint'
import prettierConfig from 'eslint-config-prettier/flat'

// 注意: eslint.config.ts (TypeScript 形式) を使う場合、devDependencies に jiti が必須。
export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },
  {
    name: 'app/files-to-ignore',
    ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**'],
  },
  pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,
  {
    rules: {
      // 型のみ import を強制 (ビルド最適化)
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
      ],
    },
  },
  // oxlint 側で有効化しているルールを ESLint 側で無効化する (二重チェック防止)。
  // 固定プリセット (flat/recommended) ではなく .oxlintrc.json の実設定から生成する。
  ...oxlint.buildFromOxlintConfigFile('./.oxlintrc.json'),
  // Prettier との競合ルールを無効化 (必ず最後に配置)
  prettierConfig,
)
