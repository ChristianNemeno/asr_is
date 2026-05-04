# Troubleshooting - OpenCode Documentation

# Troubleshooting

Common issues and how to resolve them.

To debug issues with OpenCode, start by checking the logs and local data it stores on disk.

## Logs

Log files are written to:

- **macOS/Linux:** `~/.local/share/opencode/log/`
- **Windows:** Press WIN+R and paste `%USERPROFILE%\.local\share\opencode\log`

Log files are named with timestamps (e.g., `2025-01-09T123456.log`) and the most recent 10 log files are kept.

You can set the log level with the `--log-level` command-line option to get more detailed debug information. For example, `opencode --log-level DEBUG`.

## Storage

OpenCode stores session data and other application data on disk at:

- **macOS/Linux:** `~/.local/share/opencode/`
- **Windows:** Press WIN+R and paste `%USERPROFILE%\.local\share\opencode`

This directory contains:
- `auth.json` - Authentication data like API keys, OAuth tokens
- `log/` - Application logs
- `project/` - Project-specific data like session and message data

If the project is within a Git repo, it is stored in `./<project-slug>/storage/`. If it is not a Git repo, it is stored in `./global/storage/`.

## Desktop app

OpenCode Desktop runs a local OpenCode server (the opencode-cli sidecar) in the background. Most issues are caused by a misbehaving plugin, a corrupted cache, or a bad server setting.

### Quick checks

- Fully quit and relaunch the app.
- If the app shows an error screen, click Restart and copy the error details.
- macOS only: OpenCode menu -> Reload Webview (helps if the UI is blank/frozen).

### Disable plugins

If the desktop app is crashing on launch, hanging, or behaving strangely, start by disabling plugins.

**Check the global config:** Look for a `plugin` key in your global config file.

- macOS/Linux: `~/.config/opencode/opencode.jsonc` (or `~/.config/opencode/opencode.json`)
- macOS/Linux (older installs): `~/.local/share/opencode/opencode.jsonc`
- Windows: `%USERPROFILE%\.config\opencode\opencode.jsonc`

Temporarily disable them:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [],
}
```

**Check plugin directories:** Temporarily move these out of the way (or rename the folder) and restart the desktop app:
- Global plugins: `~/.config/opencode/plugins/`
- Project plugins: `<your-project>/.opencode/plugins/`

### Clear the cache

1. Quit OpenCode Desktop completely.
2. Delete the cache directory:
   - macOS: `~/.cache/opencode`
   - Linux: `~/.cache/opencode`
   - Windows: `%USERPROFILE%\.cache\opencode`
3. Restart OpenCode Desktop.

### Fix server connection issues

If you see a "Connection Failed" dialog (or the app never gets past the splash screen):
1. From the Home screen, click the server name to open the Server picker. In the Default server section, click Clear.
2. If your `opencode.json(c)` contains a `server` section, temporarily remove it.
3. If you have `OPENCODE_PORT` set in your environment, unset it.

### Linux: Wayland / X11 issues

- If you're on Wayland and the app is blank/crashing, try launching with `OC_ALLOW_WAYLAND=1`.
- If that makes things worse, remove it and try launching under an X11 session instead.

### Windows: WebView2 runtime

On Windows, OpenCode Desktop requires the Microsoft Edge WebView2 Runtime. If the app opens to a blank window or won't start, install/update WebView2 and try again.

### Windows: General performance issues

If you're experiencing slow performance, file access issues, or terminal problems on Windows, try using WSL (Windows Subsystem for Linux).

### Notifications not showing

OpenCode Desktop only shows system notifications when:
1. Notifications are enabled for OpenCode in your OS settings, and
2. The app window is not focused.

### Reset desktop app storage (last resort)

1. Quit OpenCode Desktop.
2. Find and delete these files:
   - `opencode.settings.dat` (desktop default server URL)
   - `opencode.global.dat` and `opencode.workspace.*.dat` (UI state)
3. To find the directory:
   - macOS: `~/Library/Application Support`
   - Linux: `~/.local/share`
   - Windows: `%APPDATA%`

## Getting help

- **Report issues on GitHub:** github.com/anomalyco/opencode/issues
- **Join our Discord:** opencode.ai/discord

## Common issues

### OpenCode won't start

- Check the logs for error messages.
- Try running with `--print-logs` to see output in the terminal.
- Ensure you have the latest version with `opencode upgrade`.

### Authentication issues

- Try re-authenticating with the `/connect` command in the TUI.
- Check that your API keys are valid.
- Ensure your network allows connections to the provider's API.

### Model not available

- Check that you've authenticated with the provider.
- Verify the model name in your config is correct.
- Some models may require specific access or subscriptions.

Models should be referenced like so: `<providerId>/<modelId>`. Examples:
- `openai/gpt-4.1`
- `openrouter/google/gemini-2.5-flash`
- `opencode/kimi-k2`

To see what models you have access to, run `opencode models`.

### ProviderInitError

If you encounter a ProviderInitError, you likely have an invalid or corrupted configuration.

1. First, verify your provider is set up correctly by following the providers guide.
2. If the issue persists, try clearing your stored configuration:
   ```
   rm -rf ~/.local/share/opencode
   ```
3. Re-authenticate with your provider using the `/connect` command in the TUI.

### AI_APICallError and provider package issues

If you encounter API call errors, this may be due to outdated provider packages. OpenCode dynamically installs provider packages (OpenAI, Anthropic, Google, etc.) as needed and caches them locally.

1. Clear the provider package cache:
   ```
   rm -rf ~/.cache/opencode
   ```
2. Restart OpenCode to reinstall the latest provider packages.

### Copy/paste not working on Linux

Linux users need to have one of the following clipboard utilities installed:

**For X11 systems:**
```
apt install -y xclip
# or
apt install -y xsel
```

**For Wayland systems:**
```
apt install -y wl-clipboard
```

**For headless environments:**
```
apt install -y xvfb
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99.0
```

OpenCode will detect if you're using Wayland and prefer `wl-clipboard`, otherwise it will try to find clipboard tools in order of: `xclip` and `xsel`.
