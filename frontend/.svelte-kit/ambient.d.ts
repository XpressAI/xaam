
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * Environment variables [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env`. Like [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), this module cannot be imported into client-side code. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * _Unlike_ [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), the values exported from this module are statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * ```ts
 * import { API_KEY } from '$env/static/private';
 * ```
 * 
 * Note that all environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * 
 * ```
 * MY_FEATURE_FLAG=""
 * ```
 * 
 * You can override `.env` values from the command line like so:
 * 
 * ```bash
 * MY_FEATURE_FLAG="enabled" npm run dev
 * ```
 */
declare module '$env/static/private' {
	export const NVM_INC: string;
	export const SERP_API_KEY: string;
	export const MORPH_API_KEY: string;
	export const XAIBO_OPENAI_ORG: string;
	export const TERM_PROGRAM: string;
	export const NODE: string;
	export const INIT_CWD: string;
	export const NVM_CD_FLAGS: string;
	export const SHELL: string;
	export const LLAMA_API_KEY: string;
	export const DEEPGRAM_API_KEY: string;
	export const XPRESS_OPENAI_KEY: string;
	export const VTE_VERSION: string;
	export const TERM: string;
	export const SAVEHIST: string;
	export const HISTSIZE: string;
	export const TMPDIR: string;
	export const AKKA_LICENSE_KEY: string;
	export const DISCORD_BOT_TOKEN: string;
	export const npm_config_global_prefix: string;
	export const DISCORD_CLIENT_SECRET: string;
	export const GROQ_API_KEY: string;
	export const OPENAI_SCALA_CLIENT_ORG_ID: string;
	export const TERM_PROGRAM_VERSION: string;
	export const ATTENDEE_API_KEY: string;
	export const MallocNanoZone: string;
	export const ORIGINAL_XDG_CURRENT_DESKTOP: string;
	export const COLOR: string;
	export const XAIBO_OPENAI_API_KEY: string;
	export const OPENAI_ORG: string;
	export const npm_config_noproxy: string;
	export const SDKMAN_PLATFORM: string;
	export const npm_config_local_prefix: string;
	export const SAMBA_API_KEY: string;
	export const USER: string;
	export const NVM_DIR: string;
	export const HISTFILESIZE: string;
	export const COMMAND_MODE: string;
	export const TELEGRAM_BOT_KEY: string;
	export const OLD_ANTHROPIC_API_KEY: string;
	export const OPENAI_API_KEY: string;
	export const NEW_OPENAI_KEY: string;
	export const npm_config_globalconfig: string;
	export const SDKMAN_CANDIDATES_API: string;
	export const SSH_AUTH_SOCK: string;
	export const __CF_USER_TEXT_ENCODING: string;
	export const npm_execpath: string;
	export const PAGER: string;
	export const VECTO_VECTOR_SPACE: string;
	export const PYDEVD_DISABLE_FILE_VALIDATION: string;
	export const GITHUB_API_KEY: string;
	export const DISCORD_APP_ID: string;
	export const PATH: string;
	export const npm_package_json: string;
	export const _: string;
	export const npm_config_userconfig: string;
	export const npm_config_init_module: string;
	export const __CFBundleIdentifier: string;
	export const npm_command: string;
	export const PWD: string;
	export const JAVA_HOME: string;
	export const DISCORD_CLIENT_ID: string;
	export const CRAWLER_VECTO_TOKEN: string;
	export const npm_lifecycle_event: string;
	export const EDITOR: string;
	export const XAIBO_SLACK_CLIENT_SECRET: string;
	export const npm_package_name: string;
	export const VECTO_API_KEY: string;
	export const LANG: string;
	export const BUNDLED_DEBUGPY_PATH: string;
	export const CLOUDSDK_PYTHON: string;
	export const npm_config_npm_version: string;
	export const XPC_FLAGS: string;
	export const VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
	export const LAMBDA_API_KEY: string;
	export const XAIBO_SLACK_CLIENT_ID: string;
	export const ANTHROPIC_API_KEY: string;
	export const XAIBO_SLACK_SIGNING_SECRET: string;
	export const npm_config_node_gyp: string;
	export const npm_package_version: string;
	export const XPC_SERVICE_NAME: string;
	export const GEMINI_API_KEY: string;
	export const DISCORD_XAIBO_TOKEN: string;
	export const OPENAI_SCALA_CLIENT_API_KEY: string;
	export const VSCODE_DEBUGPY_ADAPTER_ENDPOINTS: string;
	export const HOME: string;
	export const SHLVL: string;
	export const JBANG_HOME: string;
	export const SERPER_API_KEY: string;
	export const VSCODE_GIT_ASKPASS_MAIN: string;
	export const QUARKUS_CONTAINER_IMAGE_PASSWORD: string;
	export const DISCORD_APP_TOKEN: string;
	export const npm_config_cache: string;
	export const LOGNAME: string;
	export const XAI_API_KEY: string;
	export const npm_lifecycle_script: string;
	export const SDKMAN_DIR: string;
	export const MONDAY_API_KEY: string;
	export const VSCODE_GIT_IPC_HANDLE: string;
	export const NVM_BIN: string;
	export const npm_config_user_agent: string;
	export const DISCORD_APP_KEY: string;
	export const SLACK_BOT_TOKEN: string;
	export const SDKMAN_CANDIDATES_DIR: string;
	export const PROMPT_EOL_MARK: string;
	export const GIT_ASKPASS: string;
	export const VSCODE_GIT_ASKPASS_NODE: string;
	export const DISPLAY: string;
	export const GOOGLE_AI_API_KEY: string;
	export const QUARKUS_CONTAINER_IMAGE_USERNAME: string;
	export const XPRESS_OPENAI_ORG: string;
	export const TOGETHER_AI_API_KEY: string;
	export const npm_node_execpath: string;
	export const npm_config_prefix: string;
	export const COLORTERM: string;
	export const NODE_ENV: string;
}

/**
 * Similar to [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private), except that it only includes environment variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Values are replaced statically at build time.
 * 
 * ```ts
 * import { PUBLIC_BASE_URL } from '$env/static/public';
 * ```
 */
declare module '$env/static/public' {
	
}

/**
 * This module provides access to runtime environment variables, as defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * This module cannot be imported into client-side code.
 * 
 * Dynamic environment variables cannot be used during prerendering.
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * console.log(env.DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 * 
 * > In `dev`, `$env/dynamic` always includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 */
declare module '$env/dynamic/private' {
	export const env: {
		NVM_INC: string;
		SERP_API_KEY: string;
		MORPH_API_KEY: string;
		XAIBO_OPENAI_ORG: string;
		TERM_PROGRAM: string;
		NODE: string;
		INIT_CWD: string;
		NVM_CD_FLAGS: string;
		SHELL: string;
		LLAMA_API_KEY: string;
		DEEPGRAM_API_KEY: string;
		XPRESS_OPENAI_KEY: string;
		VTE_VERSION: string;
		TERM: string;
		SAVEHIST: string;
		HISTSIZE: string;
		TMPDIR: string;
		AKKA_LICENSE_KEY: string;
		DISCORD_BOT_TOKEN: string;
		npm_config_global_prefix: string;
		DISCORD_CLIENT_SECRET: string;
		GROQ_API_KEY: string;
		OPENAI_SCALA_CLIENT_ORG_ID: string;
		TERM_PROGRAM_VERSION: string;
		ATTENDEE_API_KEY: string;
		MallocNanoZone: string;
		ORIGINAL_XDG_CURRENT_DESKTOP: string;
		COLOR: string;
		XAIBO_OPENAI_API_KEY: string;
		OPENAI_ORG: string;
		npm_config_noproxy: string;
		SDKMAN_PLATFORM: string;
		npm_config_local_prefix: string;
		SAMBA_API_KEY: string;
		USER: string;
		NVM_DIR: string;
		HISTFILESIZE: string;
		COMMAND_MODE: string;
		TELEGRAM_BOT_KEY: string;
		OLD_ANTHROPIC_API_KEY: string;
		OPENAI_API_KEY: string;
		NEW_OPENAI_KEY: string;
		npm_config_globalconfig: string;
		SDKMAN_CANDIDATES_API: string;
		SSH_AUTH_SOCK: string;
		__CF_USER_TEXT_ENCODING: string;
		npm_execpath: string;
		PAGER: string;
		VECTO_VECTOR_SPACE: string;
		PYDEVD_DISABLE_FILE_VALIDATION: string;
		GITHUB_API_KEY: string;
		DISCORD_APP_ID: string;
		PATH: string;
		npm_package_json: string;
		_: string;
		npm_config_userconfig: string;
		npm_config_init_module: string;
		__CFBundleIdentifier: string;
		npm_command: string;
		PWD: string;
		JAVA_HOME: string;
		DISCORD_CLIENT_ID: string;
		CRAWLER_VECTO_TOKEN: string;
		npm_lifecycle_event: string;
		EDITOR: string;
		XAIBO_SLACK_CLIENT_SECRET: string;
		npm_package_name: string;
		VECTO_API_KEY: string;
		LANG: string;
		BUNDLED_DEBUGPY_PATH: string;
		CLOUDSDK_PYTHON: string;
		npm_config_npm_version: string;
		XPC_FLAGS: string;
		VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
		LAMBDA_API_KEY: string;
		XAIBO_SLACK_CLIENT_ID: string;
		ANTHROPIC_API_KEY: string;
		XAIBO_SLACK_SIGNING_SECRET: string;
		npm_config_node_gyp: string;
		npm_package_version: string;
		XPC_SERVICE_NAME: string;
		GEMINI_API_KEY: string;
		DISCORD_XAIBO_TOKEN: string;
		OPENAI_SCALA_CLIENT_API_KEY: string;
		VSCODE_DEBUGPY_ADAPTER_ENDPOINTS: string;
		HOME: string;
		SHLVL: string;
		JBANG_HOME: string;
		SERPER_API_KEY: string;
		VSCODE_GIT_ASKPASS_MAIN: string;
		QUARKUS_CONTAINER_IMAGE_PASSWORD: string;
		DISCORD_APP_TOKEN: string;
		npm_config_cache: string;
		LOGNAME: string;
		XAI_API_KEY: string;
		npm_lifecycle_script: string;
		SDKMAN_DIR: string;
		MONDAY_API_KEY: string;
		VSCODE_GIT_IPC_HANDLE: string;
		NVM_BIN: string;
		npm_config_user_agent: string;
		DISCORD_APP_KEY: string;
		SLACK_BOT_TOKEN: string;
		SDKMAN_CANDIDATES_DIR: string;
		PROMPT_EOL_MARK: string;
		GIT_ASKPASS: string;
		VSCODE_GIT_ASKPASS_NODE: string;
		DISPLAY: string;
		GOOGLE_AI_API_KEY: string;
		QUARKUS_CONTAINER_IMAGE_USERNAME: string;
		XPRESS_OPENAI_ORG: string;
		TOGETHER_AI_API_KEY: string;
		npm_node_execpath: string;
		npm_config_prefix: string;
		COLORTERM: string;
		NODE_ENV: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * Similar to [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), but only includes variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Note that public dynamic environment variables must all be sent from the server to the client, causing larger network requests — when possible, use `$env/static/public` instead.
 * 
 * Dynamic environment variables cannot be used during prerendering.
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.PUBLIC_DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
