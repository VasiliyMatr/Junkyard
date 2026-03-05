-- Lua table validator
-- Receives table code as string, validates it, and returns structured result

function validate_table(lua_code)
    -- Result structure
    local result = {
        valid = false,
        error = nil,
        details = nil
    }

    -- Try to load the Lua code
    local chunk, load_error = load("return " .. lua_code)

    if not chunk then
        result.error = "Syntax error: " .. tostring(load_error)
        return result
    end

    -- Try to execute the loaded chunk
    local success, value = pcall(chunk)

    if not success then
        result.error = "Execution error: " .. tostring(value)
        return result
    end

    -- Check if the result is a table
    if type(value) ~= "table" then
        result.error = "Result is not a table, got: " .. type(value)
        return result
    end

    -- Validation successful
    result.valid = true
    result.details = "Valid Lua table with " .. count_keys(value) .. " keys"

    return result
end

-- Helper function to count table keys
function count_keys(t)
    local count = 0
    for _ in pairs(t) do
        count = count + 1
    end
    return count
end
