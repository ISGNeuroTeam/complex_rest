# check_authorization

**check_authorization** is a decorator that determines whether the user is authorized to perform a certain action on a specific object or not.

The decorator has the following signature:

```def check_authorization(action: str, when_denied: Optional[Any] = None, on_error: Optional[Callable] = None):```

To elaborate on that, it has obligatory parameter **action** that specifies the action to be performed. This action is set when decorating the function to be protected.

### It also has 2 optional parameters:
- **when_denied** - if specified, will be returned if the user has no right to perform the action on the object
- **on_error** - is a callable, if specified, it will be called if an exception is raised during **check_authorization**

### Few things to note:
- **check_authorization** only works with **BaseProtectedResource** or it's children
- args and kwargs are passed to the decorated function as well
---

### Concepts and Terminology

1. Permit - every permit can be seen as a set of **actions** and whether they are allowed or prohibited. **Role** may have one or more permits.
2. KeyChain - instance that is related to **BaseProtectedResource**. It contains **permits** that are required from **user** who wants to perform an **action** on protected resource (at least one common permit between keychain and user role is required).

---

### Before checking, many things are taken into consideration:
- if **BaseProtectedResource** has **owner_id**, it allows us to extract owner from **User** model objects. If **User** not found, **on_error** callable is trigger if provided, or standard exception is raised
- **BaseProtectedResource** has **keychain_id**, it allows us to extract keychain from **KeyChain** model objects. If **KeyChain** not found, **on_error** callable is trigger if provided, or standard exception is raised
- knowing **plugin** name from **BaseProtectedResource** and **action** name, action from **Action** model objects is retrieved
- already knowing **owner** and having **BaseProtectedResource** **user** (user who is currently using the resource), we figure out whether the user **is_owner**

### When checking, several steps are performed:
- all check are resulted in a set of booleans (None is also valid)
- for every keychain permits we filter permits that have nothing to do with our user (permit's roles don't intersect with user roles)
- when the initial filtering is done, we check all permits left on whether they allow to perform the **action**
- if the action is not listed in permit's actions we skip it (return None). Then we check ownership if **action** is flagged as **by_owner_only** 
- finally, we see if **action allows** (if True it means user is allowed else user is explicitly prohibited to perform the action)

### After checking, the decision is made either to perform an action or to return when_denied if provided or None:
- if set of booleans is empty or it has only None, we have to stick with **action default permission** because there's no way we can figure out whether the user has rights
- otherwise, we have a set of 1 to 3 possible values (True, False, None). Note that False has priority over True because, as mentioned above, if there is False, user is explicitly prohibited to perform the action. Hence if there is False -> Access is denied. To grant access the set has to contain no False.