## STEP 7 SOLUTIONS  

- How is the logged in user being kept track of?  
    - The logged in user is tracked using a session key based on the user id. If the user.id is present in the session object, then we assume they are logged in.
- What is Flask’s g object?
    - The g object is for globally namespaced data that is available for one request/response cycle.
- What is the purpose of add_user_to_g?
    - The add_user_to_g routine takes the user.id and adds it into the session object.
- What does @app.before_request mean?  
    - This operation is run before any request is sent to the server, and provides us with an opportunity to make sure the user has the sesssion['user.id'] element set, thus ensuring us that the user is authenticated into the application.