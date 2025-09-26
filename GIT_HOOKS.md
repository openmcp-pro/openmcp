# Git Hooks Documentation

This document describes the git hooks configured for the openmcp project.

## Claude Keyword Filter Hook

### Overview

The `prepare-commit-msg` hook automatically filters out lines containing the keyword "Claude" from commit messages. This ensures that commit messages remain clean and professional while still allowing the use of AI assistance during development.

### How It Works

1. **Detection**: The hook scans commit messages for the word "Claude" (case-insensitive)
2. **Filtering**: When found, it removes all lines containing "Claude" 
3. **Fallback**: If all lines are removed, it creates a default commit message: "Update code implementation"
4. **Feedback**: Provides clear console output showing what was filtered

### Features

- **Case Insensitive**: Detects "Claude", "claude", "CLAUDE", etc.
- **Line-by-Line**: Only removes lines containing the keyword, preserves other content
- **Safe Fallback**: Never leaves empty commit messages
- **Visual Feedback**: Shows before/after message content
- **Non-Intrusive**: Only activates when the keyword is detected

### Installation

The hook is already installed in this repository. For new repositories or manual installation:

```bash
# Copy the hook to your git hooks directory
cp .git/hooks/prepare-commit-msg /path/to/your/repo/.git/hooks/

# Make it executable
chmod +x /path/to/your/repo/.git/hooks/prepare-commit-msg
```

### Examples

#### Example 1: Partial Filtering
**Input:**
```
Add new authentication features
Claude helped with the implementation  
Fix localhost bypass functionality
Generated with Claude assistance
Update documentation and tests
```

**Output:**
```
Add new authentication features
Fix localhost bypass functionality
Update documentation and tests
```

#### Example 2: Complete Filtering (Fallback)
**Input:**
```
Claude helped with this implementation
Generated with Claude assistance
Claude code review
```

**Output:**
```
Update code implementation
```

#### Example 3: No Filtering Needed
**Input:**
```
Add new authentication features
Fix localhost bypass functionality
Update documentation and tests
```

**Output:** (unchanged)
```
Add new authentication features
Fix localhost bypass functionality
Update documentation and tests
```

### Console Output

When the hook activates, you'll see output like this:

```bash
⚠️  Found 'Claude' keyword in commit message. Filtering out lines containing 'Claude'...
✅ Removed lines containing 'Claude' from commit message.

📝 Filtered commit message:
==========================
Add new authentication features
Fix localhost bypass functionality
Update documentation and tests
==========================
```

### Customization

To modify the hook behavior, edit `.git/hooks/prepare-commit-msg`:

```bash
# Change the keyword to filter
grep -qi "claude" "$COMMIT_MSG_FILE"  # Change "claude" to your keyword

# Change the default fallback message
echo "Update code implementation" > "$COMMIT_MSG_FILE"  # Change the message

# Add additional keywords to filter
grep -qiE "(claude|assistant|ai)" "$COMMIT_MSG_FILE"  # Multiple keywords
```

### Disabling the Hook

To temporarily disable the hook:

```bash
# Rename the hook file
mv .git/hooks/prepare-commit-msg .git/hooks/prepare-commit-msg.disabled

# Or remove execute permission
chmod -x .git/hooks/prepare-commit-msg
```

To re-enable:

```bash
# Rename back
mv .git/hooks/prepare-commit-msg.disabled .git/hooks/prepare-commit-msg

# Or restore execute permission
chmod +x .git/hooks/prepare-commit-msg
```

### Team Setup

For teams wanting to share this hook:

1. **Option 1: Manual Installation**
   ```bash
   # Each team member runs:
   cp .git/hooks/prepare-commit-msg.template .git/hooks/prepare-commit-msg
   chmod +x .git/hooks/prepare-commit-msg
   ```

2. **Option 2: Setup Script**
   ```bash
   # Create a setup script
   #!/bin/bash
   echo "Installing git hooks..."
   cp .git/hooks/prepare-commit-msg.template .git/hooks/prepare-commit-msg
   chmod +x .git/hooks/prepare-commit-msg
   echo "✅ Git hooks installed!"
   ```

3. **Option 3: Git Config (Git 2.9+)**
   ```bash
   # Use shared hooks directory
   git config core.hooksPath .githooks/
   ```

### Troubleshooting

**Hook not running?**
- Check if the file exists: `ls -la .git/hooks/prepare-commit-msg`
- Verify execute permissions: `ls -la .git/hooks/prepare-commit-msg`
- Ensure it's executable: `chmod +x .git/hooks/prepare-commit-msg`

**Hook runs but doesn't filter?**
- Check the file encoding (should be UTF-8)
- Verify the shebang line: `#!/bin/bash`
- Test manually: `.git/hooks/prepare-commit-msg /tmp/test_msg message`

**Want to see what would be filtered without committing?**
```bash
# Test the hook manually
echo "Test commit with Claude assistance" > /tmp/test_msg
.git/hooks/prepare-commit-msg /tmp/test_msg message
cat /tmp/test_msg
```

### Security Note

This hook processes commit messages but doesn't modify your actual code files. It only affects the commit metadata stored in git history.