# Settings System - Comprehensive Test Plan

**Created:** 2025-01-15
**Version:** 1.0
**Status:** Phase 2 Complete - Ready for Testing
**Purpose:** Comprehensive testing guide for all settings system features

---

## 📋 TABLE OF CONTENTS

1. [Test Environment Setup](#test-environment-setup)
2. [Phase 1 Tests: Settings Window](#phase-1-tests-settings-window)
3. [Phase 2 Tests: Preset Management](#phase-2-tests-preset-management)
4. [Integration Tests](#integration-tests)
5. [Edge Case Tests](#edge-case-tests)
6. [Performance Tests](#performance-tests)
7. [Bug Reporting Template](#bug-reporting-template)

---

## TEST ENVIRONMENT SETUP

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] FFmpeg installed and accessible
- [ ] Application runs without errors: `python src/main_phase2.py`

### Before Testing
1. **Backup existing configuration:**
   ```bash
   cp config/settings.json config/settings.json.backup
   cp config/default_presets.json config/default_presets.json.backup
   ```

2. **Create fresh test environment (optional):**
   ```bash
   # Delete existing config to start fresh
   rm config/settings.json
   # Application will recreate with defaults
   ```

3. **Launch application:**
   ```bash
   python src/main_phase2.py
   # OR
   run_phase2.bat
   ```

---

## PHASE 1 TESTS: SETTINGS WINDOW

### Test 1.1: Settings Window Opening

**Objective:** Verify settings window opens correctly

**Steps:**
1. Click ⚙️ (settings) button in top-right of main window
2. Observe settings window appearance

**Expected Results:**
- [ ] Settings window opens as modal dialog (main window blocked)
- [ ] Window size is 900x650 pixels
- [ ] Window is centered on screen
- [ ] Window title is "Settings"
- [ ] All 6 tabs are visible in tab bar

**Pass/Fail:** ___________

**Notes:** ___________________________________________

---

### Test 1.2: Tab Navigation

**Objective:** Verify all tabs are accessible and display correctly

**Steps:**
1. Click each tab in sequence:
   - 🎬 Compression Presets
   - 💾 Output & Naming
   - 🔧 Behavior
   - 🎭 Scene Detection
   - 📁 Default Paths
   - ℹ️ About

2. For each tab, verify:
   - Tab switches without errors
   - Content displays correctly
   - No overlapping elements
   - Controls are enabled and functional

**Expected Results:**
- [ ] All 6 tabs switch correctly
- [ ] Each tab displays its specific content
- [ ] No visual glitches or overlapping
- [ ] All controls are properly aligned

**Pass/Fail:** ___________

**Notes:** ___________________________________________

---

### Test 1.3: Output & Naming Tab

**Objective:** Verify folder naming and template system

**Test 1.3.1: Real-time Preview**

**Steps:**
1. Navigate to "Output & Naming" tab
2. Modify "Masters Folder" name: `Masters` → `Master-Files`
3. Observe preview panel (bottom of tab)

**Expected Results:**
- [ ] Preview updates **immediately** (real-time)
- [ ] New folder name appears in preview: `Master-Files/`
- [ ] Preview shows example structure with all folder changes

**Pass/Fail:** ___________

---

**Test 1.3.2: Project Folder Template**

**Steps:**
1. Change project folder template: `{date}_{artwork}` → `{artwork}-{date}`
2. Observe preview

**Expected Results:**
- [ ] Preview shows new format: `ArtworkName-25-01-15/`
- [ ] Template variables are correctly substituted
- [ ] Preview updates in real-time

**Pass/Fail:** ___________

---

**Test 1.3.3: File Naming Template**

**Steps:**
1. Change file template: `{artwork}_{type}_{seq}_{aspect}` → `{type}-{seq}`
2. Observe preview

**Expected Results:**
- [ ] Preview shows simplified names: `HQ-01.png`, `compressed-02.jpg`
- [ ] Preview updates in real-time
- [ ] All template variables work correctly

**Pass/Fail:** ___________

---

**Test 1.3.4: Reset to Defaults**

**Steps:**
1. Modify several folder names and templates
2. Click "Reset to Defaults" button
3. Observe all fields

**Expected Results:**
- [ ] All fields revert to original defaults
- [ ] Preview updates to show default structure
- [ ] Confirmation message appears (if implemented)

**Pass/Fail:** ___________

---

### Test 1.4: Behavior Tab

**Objective:** Verify behavior settings controls

**Steps:**
1. Navigate to "Behavior" tab
2. Toggle "Auto-open output folder" checkbox
3. Toggle "Generate process log" checkbox
4. Select different encoder options (x264 / NVENC)

**Expected Results:**
- [ ] Both checkboxes toggle correctly
- [ ] Radio buttons switch encoder selection
- [ ] Only one radio button selected at a time
- [ ] Settings are visually reflected immediately

**Pass/Fail:** ___________

---

### Test 1.5: Scene Detection Tab

**Objective:** Verify integer-only slider and spinbox

**Test 1.5.1: Threshold Slider**

**Steps:**
1. Navigate to "Scene Detection" tab
2. Drag threshold slider left and right
3. Observe value display

**Expected Results:**
- [ ] Slider moves smoothly
- [ ] Value displays **integers only** (no decimals like 1.234)
- [ ] Range is 1-100
- [ ] Value label updates in real-time

**Pass/Fail:** ___________

---

**Test 1.5.2: Min Scene Length Spinbox**

**Steps:**
1. Click up/down arrows in spinbox
2. Type a value directly (e.g., 50)
3. Try typing invalid values (e.g., 200, -5)

**Expected Results:**
- [ ] Spinbox increments/decrements correctly
- [ ] Range is 1-120 frames
- [ ] Invalid values are rejected or clamped to range
- [ ] Value is always an integer

**Pass/Fail:** ___________

---

### Test 1.6: Default Paths Tab

**Objective:** Verify directory selection

**Test 1.6.1: Output Directory**

**Steps:**
1. Navigate to "Default Paths" tab
2. Click "Browse..." button for output directory
3. Select a valid folder
4. Observe path display

**Expected Results:**
- [ ] Folder dialog opens
- [ ] Selected path displays in text field
- [ ] Path is absolute (full path shown)
- [ ] Invalid paths are rejected (if validation implemented)

**Pass/Fail:** ___________

---

**Test 1.6.2: R&D Directory**

**Steps:**
1. Click "Browse..." button for R&D directory
2. Select a valid folder
3. Observe path display

**Expected Results:**
- [ ] Folder dialog opens
- [ ] Selected path displays in text field
- [ ] Path is absolute

**Pass/Fail:** ___________

---

### Test 1.7: About Tab

**Objective:** Verify information display

**Steps:**
1. Navigate to "About" tab
2. Read displayed information

**Expected Results:**
- [ ] App name and version displayed
- [ ] Copyright information shown
- [ ] FFmpeg status shown (✓ or ✗)
- [ ] System information section present
- [ ] All text is readable and properly formatted

**Pass/Fail:** ___________

---

### Test 1.8: Save and Cancel

**Test 1.8.1: Save Changes**

**Steps:**
1. Modify settings in multiple tabs (naming, behavior, scene detection)
2. Click "Save" button
3. Observe window behavior
4. Reopen settings window

**Expected Results:**
- [ ] Success message appears (or silent save)
- [ ] Settings window closes
- [ ] Main window becomes active again
- [ ] Reopening settings shows saved changes
- [ ] `config/settings.json` file updated

**Pass/Fail:** ___________

---

**Test 1.8.2: Cancel Changes**

**Steps:**
1. Modify settings in multiple tabs
2. Click "Cancel" button
3. Reopen settings window

**Expected Results:**
- [ ] No confirmation dialog (changes discarded silently)
- [ ] Settings window closes
- [ ] Reopening settings shows **original** values (no changes)
- [ ] `config/settings.json` file unchanged

**Pass/Fail:** ___________

---

### Test 1.9: Settings Persistence

**Objective:** Verify settings persist across app restarts

**Steps:**
1. Modify all settings tabs with unique values
2. Click "Save"
3. Close entire application
4. Restart application: `python src/main_phase2.py`
5. Open settings window

**Expected Results:**
- [ ] All modified settings are preserved
- [ ] Naming templates match saved values
- [ ] Behavior checkboxes match saved state
- [ ] Scene detection values match saved values
- [ ] Paths match saved directories
- [ ] No settings reverted to defaults

**Pass/Fail:** ___________

**Notes:** ___________________________________________

---

## PHASE 2 TESTS: PRESET MANAGEMENT

### Test 2.1: Preset List Display

**Objective:** Verify preset list shows all presets correctly

**Steps:**
1. Navigate to "Compression Presets" tab
2. Observe preset list (treeview)

**Expected Results:**
- [ ] All 3 built-in presets are displayed:
  - Webflow Standard
  - Retina/Web Showcase
  - Ultra-Light Web
- [ ] Columns show: Name, Description, Quality, Type
- [ ] "Type" column shows "Built-in" for default presets
- [ ] Double-click on preset selects it (no action yet)

**Pass/Fail:** ___________

---

### Test 2.2: New Preset

**Test 2.2.1: Create New Preset**

**Steps:**
1. Click "➕ New Preset" button
2. Observe preset editor window

**Expected Results:**
- [ ] Preset editor window opens (modal)
- [ ] Window title is "Preset Editor - New Preset"
- [ ] All 5 settings tabs are visible:
  - Stills HQ
  - Stills Web
  - Video Encoding
  - Audio
  - Thumbnails
- [ ] Default values are populated in all fields
- [ ] Name field shows "New Preset" or is empty

**Pass/Fail:** ___________

---

**Test 2.2.2: Customize New Preset**

**Steps:**
1. Change preset name: "My Custom Preset"
2. Change description: "High quality for archival"
3. Navigate to "Video Encoding" tab
4. Change CRF value: 18
5. Observe quality indicator

**Expected Results:**
- [ ] Name and description fields accept text
- [ ] Video Encoding tab loads correctly
- [ ] CRF slider moves to 18
- [ ] Quality indicator shows "High Quality" (green color)
- [ ] No errors or warnings

**Pass/Fail:** ___________

---

**Test 2.2.3: Save New Preset**

**Steps:**
1. Click "Save Preset" button
2. Observe messages and window behavior
3. Check preset list in settings window

**Expected Results:**
- [ ] Success message appears: "Preset '{name}' created successfully!"
- [ ] Preset editor closes
- [ ] Settings window is still open
- [ ] New preset appears in preset list
- [ ] New preset shows "Type: Custom"
- [ ] Preset list refreshes automatically

**Pass/Fail:** ___________

---

**Test 2.2.4: Validate Empty Name**

**Steps:**
1. Click "➕ New Preset"
2. Leave name field empty
3. Click "Save Preset"

**Expected Results:**
- [ ] Error message: "Preset name cannot be empty"
- [ ] Preset editor remains open
- [ ] No preset is created

**Pass/Fail:** ___________

---

**Test 2.2.5: Validate At Least One Output**

**Steps:**
1. Click "➕ New Preset"
2. Disable all output types (uncheck all "Enabled" checkboxes)
3. Click "Save Preset"

**Expected Results:**
- [ ] Error message: "At least one output type must be enabled"
- [ ] Preset editor remains open
- [ ] No preset is created

**Pass/Fail:** ___________

---

### Test 2.3: Edit Preset

**Test 2.3.1: Edit Custom Preset**

**Steps:**
1. Select a custom preset from list (created in Test 2.2)
2. Click "✏️ Edit" button
3. Observe preset editor

**Expected Results:**
- [ ] Preset editor opens in edit mode
- [ ] Window title is "Preset Editor - Edit Preset"
- [ ] All fields are populated with current preset values
- [ ] Name, description, and all settings match the preset
- [ ] All tabs show correct values

**Pass/Fail:** ___________

---

**Test 2.3.2: Modify and Save Custom Preset**

**Steps:**
1. Change preset name: "My Custom Preset V2"
2. Change CRF value: 20
3. Click "Save Preset"
4. Check preset list

**Expected Results:**
- [ ] Success message: "Preset '{name}' updated successfully!"
- [ ] Preset editor closes
- [ ] Preset list shows updated name
- [ ] Reopening preset editor shows new CRF value (20)

**Pass/Fail:** ___________

---

**Test 2.3.3: Attempt to Edit Built-in Preset**

**Steps:**
1. Select "Webflow Standard" preset (built-in)
2. Click "✏️ Edit" button
3. Observe dialog

**Expected Results:**
- [ ] Dialog appears: "Built-in presets cannot be edited. Would you like to duplicate this preset and edit the copy?"
- [ ] Two buttons: "Yes" and "No"
- [ ] Clicking "No" closes dialog, no action
- [ ] Clicking "Yes" opens duplicate workflow (Test 2.4)

**Pass/Fail:** ___________

---

### Test 2.4: Duplicate Preset

**Test 2.4.1: Duplicate Built-in Preset**

**Steps:**
1. Select "Retina/Web Showcase" preset
2. Click "📋 Duplicate" button
3. Observe preset editor

**Expected Results:**
- [ ] Preset editor opens with duplicated values
- [ ] Window title is "Preset Editor - New Preset"
- [ ] Name shows: "Retina/Web Showcase (Copy)"
- [ ] All settings match the original preset
- [ ] ID is different (new unique ID generated)
- [ ] Editable flag is `true`

**Pass/Fail:** ___________

---

**Test 2.4.2: Customize and Save Duplicate**

**Steps:**
1. Change name to remove "(Copy)": "My Retina Preset"
2. Modify some settings (e.g., change CRF)
3. Click "Save Preset"
4. Check preset list

**Expected Results:**
- [ ] Success message appears
- [ ] New preset appears in list with new name
- [ ] Type shows "Custom"
- [ ] Original "Retina/Web Showcase" is unchanged

**Pass/Fail:** ___________

---

**Test 2.4.3: Duplicate Custom Preset**

**Steps:**
1. Select a custom preset
2. Click "📋 Duplicate"
3. Observe and save

**Expected Results:**
- [ ] Works same as duplicating built-in preset
- [ ] Name gets "(Copy)" suffix
- [ ] New unique ID generated
- [ ] Both custom presets exist after save

**Pass/Fail:** ___________

---

### Test 2.5: Delete Preset

**Test 2.5.1: Delete Custom Preset**

**Steps:**
1. Select a custom preset
2. Click "🗑️ Delete" button
3. Observe confirmation dialog

**Expected Results:**
- [ ] Confirmation dialog appears
- [ ] Message: "Delete preset '{name}'? This action cannot be undone."
- [ ] Two buttons: "Delete" and "Cancel"

**Pass/Fail:** ___________

---

**Test 2.5.2: Confirm Deletion**

**Steps:**
1. Click "Delete" in confirmation dialog
2. Observe preset list

**Expected Results:**
- [ ] Success message: "Preset '{name}' deleted successfully!"
- [ ] Preset disappears from list immediately
- [ ] Remaining presets are still displayed
- [ ] No errors

**Pass/Fail:** ___________

---

**Test 2.5.3: Cancel Deletion**

**Steps:**
1. Select a custom preset
2. Click "🗑️ Delete"
3. Click "Cancel" in confirmation

**Expected Results:**
- [ ] Dialog closes
- [ ] Preset remains in list (not deleted)
- [ ] No messages or errors

**Pass/Fail:** ___________

---

**Test 2.5.4: Attempt to Delete Built-in Preset**

**Steps:**
1. Select "Webflow Standard" preset
2. Click "🗑️ Delete" button

**Expected Results:**
- [ ] Error message: "Built-in presets cannot be deleted. You can duplicate it to create a custom version."
- [ ] No confirmation dialog
- [ ] Preset remains in list

**Pass/Fail:** ___________

---

### Test 2.6: Import Preset

**Test 2.6.1: Prepare Test JSON File**

**Steps:**
1. Export an existing preset (see Test 2.7)
2. Manually create a valid JSON file:

```json
{
  "id": "test_import_preset",
  "name": "Imported Test Preset",
  "description": "Testing import functionality",
  "editable": true,
  "settings": {
    "stills_hq": {"enabled": true, "format": "PNG"},
    "stills_web": {"enabled": true, "quality": 85},
    "video": {"crf": 22, "preset": "medium"},
    "audio": {"bitrate": "192k"},
    "thumbnails": {"enabled": true, "quality": 80}
  }
}
```

**Expected Results:**
- [ ] JSON file created successfully
- [ ] JSON is valid (no syntax errors)

**Pass/Fail:** ___________

---

**Test 2.6.2: Import Valid Preset**

**Steps:**
1. Click "📥 Import" button
2. Select the test JSON file created above
3. Observe messages and preset list

**Expected Results:**
- [ ] File dialog opens
- [ ] After selecting file, success message: "Preset '{name}' imported successfully!"
- [ ] Imported preset appears in list
- [ ] Type shows "Custom"
- [ ] Opening preset editor shows all imported settings

**Pass/Fail:** ___________

---

**Test 2.6.3: Import with ID Conflict**

**Steps:**
1. Import the same JSON file again (ID already exists)
2. Observe behavior

**Expected Results:**
- [ ] Info dialog: "A preset with this ID already exists. The imported preset has been renamed to '{new_id}'."
- [ ] Imported preset appears with modified ID (e.g., `test_import_preset_imported_1234567890`)
- [ ] Name may have "(Imported)" suffix
- [ ] Both presets exist in list

**Pass/Fail:** ___________

---

**Test 2.6.4: Import Invalid JSON**

**Steps:**
1. Create a text file with invalid JSON:
```
{ "invalid": json syntax }
```
2. Try to import this file

**Expected Results:**
- [ ] Error message: "The file is not a valid JSON file"
- [ ] No preset is imported
- [ ] Preset list unchanged

**Pass/Fail:** ___________

---

**Test 2.6.5: Import Missing Required Fields**

**Steps:**
1. Create JSON file missing required fields:
```json
{
  "name": "Incomplete Preset"
}
```
2. Try to import

**Expected Results:**
- [ ] Error message: "Missing required fields: id, settings" (or similar)
- [ ] No preset imported
- [ ] Preset list unchanged

**Pass/Fail:** ___________

---

### Test 2.7: Export Preset

**Test 2.7.1: Export Built-in Preset**

**Steps:**
1. Select "Webflow Standard" preset
2. Click "💾 Export" button
3. Choose save location (e.g., Desktop)
4. Accept default filename or customize

**Expected Results:**
- [ ] Save file dialog opens
- [ ] Default filename is: `Webflow_Standard.json` (spaces replaced with underscores)
- [ ] `.json` extension is automatically added if not present
- [ ] After saving, success message: "Preset exported to {filepath}"

**Pass/Fail:** ___________

---

**Test 2.7.2: Verify Exported File**

**Steps:**
1. Open the exported JSON file in a text editor
2. Validate structure

**Expected Results:**
- [ ] JSON is valid and parsable
- [ ] Pretty-formatted with indentation (indent=2)
- [ ] Contains all required fields: `id`, `name`, `description`, `editable`, `settings`
- [ ] Settings section contains all 5 output types
- [ ] All values match the original preset

**Pass/Fail:** ___________

---

**Test 2.7.3: Re-import Exported Preset**

**Steps:**
1. Import the exported JSON file from Test 2.7.1
2. Compare values

**Expected Results:**
- [ ] Import succeeds
- [ ] Imported preset has all the same settings as original
- [ ] No data loss during export/import cycle

**Pass/Fail:** ___________

---

**Test 2.7.4: Export Custom Preset**

**Steps:**
1. Select a custom preset
2. Export to file
3. Verify file contents

**Expected Results:**
- [ ] Works same as exporting built-in preset
- [ ] All custom settings are preserved in export
- [ ] `editable: true` in exported JSON

**Pass/Fail:** ___________

---

### Test 2.8: Preset Editor - Detailed Controls

**Test 2.8.1: Stills HQ Tab**

**Steps:**
1. Create new preset
2. Navigate to "Stills HQ" tab
3. Test all controls

**Expected Results:**
- [ ] "Enabled" checkbox toggles correctly
- [ ] Format shows "PNG" (fixed, readonly)
- [ ] Resolution dropdown has options: Source, Custom
- [ ] Color Space dropdown has: Source, sRGB, Adobe RGB
- [ ] All controls are functional

**Pass/Fail:** ___________

---

**Test 2.8.2: Stills Web Tab**

**Steps:**
1. Navigate to "Stills Web" tab
2. Test all controls

**Expected Results:**
- [ ] "Enabled" checkbox toggles
- [ ] Quality slider: 1-100 range
- [ ] Quality value displays in real-time
- [ ] Max Width dropdown: source, 1920, 2560, 3840, custom
- [ ] Progressive JPEG checkbox toggles
- [ ] Optimize encoding checkbox toggles
- [ ] Color Space dropdown: Source, sRGB
- [ ] Chroma Subsampling dropdown: 4:4:4, 4:2:2, 4:2:0

**Pass/Fail:** ___________

---

**Test 2.8.3: Video Encoding Tab - CRF Quality Indicators**

**Steps:**
1. Navigate to "Video Encoding" tab
2. Move CRF slider to different values:
   - CRF 10 (near-lossless range)
   - CRF 20 (high quality range)
   - CRF 26 (medium quality range)
   - CRF 35 (low quality range)

**Expected Results:**
- [ ] **CRF 0-17:** Label shows "Lossless / Near-Lossless" in **blue** color
- [ ] **CRF 18-23:** Label shows "High Quality" in **green** color
- [ ] **CRF 24-28:** Label shows "Medium Quality" in **orange** color
- [ ] **CRF 29+:** Label shows "Low Quality / Small File" in **red** color
- [ ] Label updates **in real-time** as slider moves

**Pass/Fail:** ___________

---

**Test 2.8.4: Video Encoding Tab - All Controls**

**Steps:**
1. Test all video encoding controls

**Expected Results:**
- [ ] Codec shows "H.264" (fixed, readonly)
- [ ] Resolution dropdown: source, 1080p, 1440p, 4K, custom
- [ ] CRF slider: 0-51 range
- [ ] Encoding preset dropdown: ultrafast → veryslow (9 options)
- [ ] Profile dropdown: baseline, main, high
- [ ] Level dropdown: 3.0, 3.1, 4.0, 4.1, 5.0, 5.1
- [ ] Pixel Format dropdown: yuv420p, yuv422p, yuv444p
- [ ] FPS dropdown: source, 24, 25, 30, 50, 60, custom
- [ ] Two-pass encoding checkbox toggles
- [ ] "Enabled" checkbox toggles

**Pass/Fail:** ___________

---

**Test 2.8.5: Audio Tab**

**Steps:**
1. Navigate to "Audio" tab
2. Test all controls

**Expected Results:**
- [ ] Codec shows "AAC" (fixed, readonly)
- [ ] Bitrate dropdown: 128k, 192k, 256k, 320k, custom
- [ ] Sample Rate dropdown: 44100, 48000, 96000
- [ ] Channels dropdown: mono, stereo, source
- [ ] All dropdowns work correctly

**Pass/Fail:** ___________

---

**Test 2.8.6: Thumbnails Tab**

**Steps:**
1. Navigate to "Thumbnails" tab
2. Test all controls

**Expected Results:**
- [ ] "Enabled" checkbox toggles
- [ ] Format dropdown: JPEG, PNG
- [ ] Quality slider: 1-100 range
- [ ] Quality value displays in real-time
- [ ] Max Width dropdown: 400, 800, 1200, custom
- [ ] All controls functional

**Pass/Fail:** ___________

---

## INTEGRATION TESTS

### Test 3.1: Main Window Preset Dropdown

**Objective:** Verify preset dropdown in main window integrates with settings

**Test 3.1.1: Initial Load**

**Steps:**
1. Launch application
2. Observe preset dropdown in main window

**Expected Results:**
- [ ] Dropdown shows all available presets (built-in + custom)
- [ ] Default preset is selected (first in list or last used)
- [ ] Dropdown is populated correctly

**Pass/Fail:** ___________

---

**Test 3.1.2: Preset Dropdown Refresh After New Preset**

**Steps:**
1. Note current presets in main window dropdown
2. Open Settings → Create new preset
3. Save preset
4. Close settings window
5. Check main window dropdown

**Expected Results:**
- [ ] Dropdown automatically refreshes (no manual refresh needed)
- [ ] New preset appears in dropdown
- [ ] All existing presets are still present
- [ ] Dropdown is functional

**Pass/Fail:** ___________

---

**Test 3.1.3: Preset Dropdown Refresh After Edit**

**Steps:**
1. Open Settings → Edit a custom preset name
2. Save changes
3. Close settings window
4. Check main window dropdown

**Expected Results:**
- [ ] Dropdown shows updated preset name
- [ ] No duplicates
- [ ] Previous selection is maintained (if possible)

**Pass/Fail:** ___________

---

**Test 3.1.4: Preset Dropdown Refresh After Delete**

**Steps:**
1. Select a custom preset in main window dropdown
2. Open Settings → Delete that preset
3. Close settings window
4. Check main window dropdown

**Expected Results:**
- [ ] Deleted preset is removed from dropdown
- [ ] Dropdown auto-selects a different preset (first available)
- [ ] No errors or blank selection

**Pass/Fail:** ___________

---

### Test 3.2: End-to-End Processing

**Objective:** Verify custom presets are used correctly during processing

**Test 3.2.1: Process with Custom Preset**

**Steps:**
1. Create a custom preset with distinctive settings:
   - CRF: 18 (high quality)
   - Stills Web Quality: 95
   - Video Resolution: 1080p
2. Save preset
3. Select this preset in main window dropdown
4. Select a master video file
5. Run full processing pipeline

**Expected Results:**
- [ ] Processing completes without errors
- [ ] Process log shows the custom preset was used
- [ ] Output video has CRF 18 (verify with ffprobe if possible)
- [ ] Output stills have quality 95 (verify file size is high)
- [ ] All settings from preset are applied correctly

**Pass/Fail:** ___________

**Notes:** ___________________________________________

---

**Test 3.2.2: Switch Presets and Reprocess**

**Steps:**
1. Process with "Webflow Standard" preset
2. Note output file sizes and quality
3. Switch to "Ultra-Light Web" preset
4. Process the same video again
5. Compare outputs

**Expected Results:**
- [ ] Different presets produce different output characteristics
- [ ] Ultra-Light Web produces smaller files
- [ ] File sizes and quality differ as expected per preset settings
- [ ] No errors during processing

**Pass/Fail:** ___________

**Notes:** ___________________________________________

---

### Test 3.3: Settings Persistence Across Sessions

**Objective:** Verify all settings persist correctly

**Test 3.3.1: Full Persistence Test**

**Steps:**
1. Modify ALL settings:
   - Create 2 custom presets
   - Change naming templates
   - Change behavior settings
   - Change scene detection values
   - Change default paths
2. Save settings
3. Note all changed values
4. Close application completely
5. Restart application
6. Open settings window
7. Check all tabs

**Expected Results:**
- [ ] All 2 custom presets exist
- [ ] Naming templates match saved values
- [ ] Behavior checkboxes match saved state
- [ ] Scene detection values match
- [ ] Default paths match
- [ ] NO settings reverted to defaults
- [ ] All custom presets are editable
- [ ] Built-in presets are unchanged

**Pass/Fail:** ___________

**Notes:** ___________________________________________

---

## EDGE CASE TESTS

### Test 4.1: Rapid Operations

**Test 4.1.1: Rapid Tab Switching**

**Steps:**
1. Open settings window
2. Rapidly click through all tabs multiple times
3. Observe for errors or glitches

**Expected Results:**
- [ ] No errors or crashes
- [ ] All tabs load correctly
- [ ] No visual glitches
- [ ] Performance is acceptable

**Pass/Fail:** ___________

---

**Test 4.1.2: Rapid Preset Creation**

**Steps:**
1. Create 5 new presets in quick succession
2. Save each one immediately

**Expected Results:**
- [ ] All 5 presets are created successfully
- [ ] Each has a unique ID
- [ ] Preset list shows all 5
- [ ] No duplicate IDs or names

**Pass/Fail:** ___________

---

### Test 4.2: Boundary Values

**Test 4.2.1: CRF Boundaries**

**Steps:**
1. Create new preset
2. Set CRF to minimum: 0
3. Set CRF to maximum: 51
4. Try to set CRF beyond range (if possible)

**Expected Results:**
- [ ] CRF 0 accepted, quality indicator correct
- [ ] CRF 51 accepted, quality indicator correct
- [ ] Values beyond 0-51 are rejected or clamped

**Pass/Fail:** ___________

---

**Test 4.2.2: Quality Slider Boundaries**

**Steps:**
1. Set Stills Web quality to 1 (minimum)
2. Set quality to 100 (maximum)
3. Try invalid values

**Expected Results:**
- [ ] Quality 1 accepted
- [ ] Quality 100 accepted
- [ ] Values beyond 1-100 rejected or clamped

**Pass/Fail:** ___________

---

### Test 4.3: Special Characters

**Test 4.3.1: Preset Names with Special Characters**

**Steps:**
1. Create preset with name: `Test-Preset_v2 (FINAL) [2024]`
2. Save and export

**Expected Results:**
- [ ] Preset saves successfully
- [ ] Name displays correctly in list
- [ ] Export filename handles special characters appropriately
- [ ] No errors

**Pass/Fail:** ___________

---

**Test 4.3.2: Paths with Spaces and Unicode**

**Steps:**
1. Set default output path to: `C:\Users\Test User\My Documents\Видео\`
2. Save settings
3. Restart application

**Expected Results:**
- [ ] Path with spaces and Unicode characters is accepted
- [ ] Path persists correctly
- [ ] Path displays correctly after reload

**Pass/Fail:** ___________

---

### Test 4.4: Empty States

**Test 4.4.1: No Custom Presets**

**Steps:**
1. Delete all custom presets
2. Observe preset list with only built-in presets

**Expected Results:**
- [ ] Built-in presets are always visible
- [ ] No errors when only built-in presets exist
- [ ] All CRUD buttons remain functional

**Pass/Fail:** ___________

---

### Test 4.5: Large Number of Presets

**Test 4.5.1: Many Custom Presets**

**Steps:**
1. Create 20 custom presets
2. Observe preset list and dropdown behavior

**Expected Results:**
- [ ] Preset list accommodates many presets
- [ ] Scrollbar appears if needed
- [ ] Performance remains acceptable
- [ ] Main window dropdown shows all presets (with scrolling)

**Pass/Fail:** ___________

---

## PERFORMANCE TESTS

### Test 5.1: Response Time

**Objective:** Verify UI responsiveness

**Test 5.1.1: Settings Window Open Time**

**Steps:**
1. Click settings button
2. Measure time until window fully loads

**Expected Results:**
- [ ] Settings window opens in < 2 seconds
- [ ] All tabs and content load quickly
- [ ] No noticeable lag

**Pass/Fail:** ___________

---

**Test 5.1.2: Preset Editor Open Time**

**Steps:**
1. Click "➕ New Preset" or "✏️ Edit"
2. Measure time until editor fully loads

**Expected Results:**
- [ ] Preset editor opens in < 1 second
- [ ] All tabs and controls load quickly

**Pass/Fail:** ___________

---

### Test 5.2: Save Performance

**Test 5.2.1: Save Time with Many Presets**

**Steps:**
1. Create 20 custom presets
2. Modify settings
3. Click "Save"
4. Measure time until save completes

**Expected Results:**
- [ ] Save completes in < 3 seconds
- [ ] Success message appears promptly
- [ ] No freezing or lag

**Pass/Fail:** ___________

---

## BUG REPORTING TEMPLATE

When you find a bug, please document using this template:

---

### Bug Report #___

**Date:** ___________
**Tester:** ___________

**Test ID:** ___________ (e.g., Test 2.3.1)

**Bug Title:** ___________________________________________

**Severity:**
- [ ] Critical (crashes, data loss)
- [ ] High (feature doesn't work)
- [ ] Medium (works but with issues)
- [ ] Low (cosmetic, minor annoyance)

**Steps to Reproduce:**
1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

**Expected Behavior:**
___________________________________________

**Actual Behavior:**
___________________________________________

**Screenshots/Logs:**
(Attach screenshots or paste error logs here)

**Environment:**
- OS: ___________
- Python Version: ___________
- Application Version: ___________

**Additional Notes:**
___________________________________________

---

## TEST SUMMARY

**Test Date:** ___________
**Tester Name:** ___________
**Total Tests:** ___________
**Tests Passed:** ___________
**Tests Failed:** ___________
**Tests Skipped:** ___________

**Overall Pass Rate:** ___________%

**Critical Bugs Found:** ___________
**Recommendation:**
- [ ] Ready for production
- [ ] Needs bug fixes before release
- [ ] Requires major rework

**Notes:**
___________________________________________
___________________________________________
___________________________________________

---

**Document Version:** 1.0
**Last Updated:** 2025-01-15
**Status:** Ready for Testing
