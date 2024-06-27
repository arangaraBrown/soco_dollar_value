css_style = """

body {
    background-color: var(--background-color);
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
    font-size: 0.4em; /* Scale down font size */
}

.question-box {
    background-color: var(--box-color);
    padding: 8px 8px 24px 8px; /* Scale down padding */
    width: 32%; /* Scale down width */
    min-width: 280px; /* Scale down min-width */
    position: relative;
    border-radius: 4px; /* Scale down border-radius */
    box-shadow: 0 0 4px rgba(0, 0, 0, 0.1); /* Scale down box-shadow */
}

.question-text {
    text-align: center;
    margin-bottom: 11px; /* Scale down margin-bottom */
    font-size: 0.4em; /* Adjust font size if needed */
    color: #04362c;
}

.options {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
    width: 100%;
    margin: 8px 0; /* Scale down margin */
}

.radio-container {
    display: block;
    position: relative;
    cursor: pointer;
    user-select: none;
    width: 45%;
    text-align: center;
    margin: 0 4px; /* Scale down margin */
    border: 1px solid var(--option-color);
    border-radius: 4px; /* Scale down border-radius */
    padding: 4px; /* Scale down padding */
    background-color: #fff;
    transition: background-color 0.3s;
}

.radio-container input {
    position: absolute;
    opacity: 0;
    cursor: pointer;
    height: 0;
    width: 0;
}

.radio-checkmark {
    display: block;
    padding: 4px; /* Scale down padding */
    color: #04362c;
}

.radio-container:hover {
    background-color: var(--hover-color);
}

.radio-container input:checked~.radio-checkmark {
    background-color: var(--alt-color);
    color: #fff;
    border-radius: 2px; /* Scale down border-radius */
}

#next-button {
    display: none;
    background-color: var(--alt-color);
    color: white;
    border: none;
    padding: 4px 8px; /* Scale down padding */
    border-radius: 1.6px; /* Scale down border-radius */
    cursor: pointer;
    align-self: flex-end;
}

#next-button:disabled {
    background-color: var(--hover-color);
    cursor: not-allowed;
}

body {
    font-family: Arial, sans-serif;
    background-color: #FFFFFF;
    color: #4A4A4A;
    margin: 0;
    padding: 8px; /* Scale down padding */
}

h1 {
    color: #4A4A4A;
    font-size: 1.2em; /* Adjust font size if needed */
}

form {
    background-color: #F2F2F2;
    padding: 8px; /* Scale down padding */
    border-radius: 4px; /* Scale down border-radius */
    box-shadow: 0 0 4px rgba(0, 0, 0, 0.1); /* Scale down box-shadow */
}

p {
    margin: 4px 0; /* Scale down margin */
    font-size: 0.4em; /* Scale down font size */
}

select, input[type="submit"], input[type="number"], input[type="text"] {
    width: 100%;
    padding: 4px; /* Scale down padding */
    margin: 4px 0; /* Scale down margin */
    border: 1px solid #4A4A4A;
    border-radius: 2px; /* Scale down border-radius */
    background-color: #FFFFFF;
    color: #4A4A4A;
    font-size: 0.4em; /* Scale down font size */
}

input[type="submit"] {
    background-color: #FFC107;
    color: #4A4A4A;
    cursor: pointer;
    font-weight: bold;
    border: none;
}

input[type="submit"]:hover {
    background-color: #E0A800;
}

"""
