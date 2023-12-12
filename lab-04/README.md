# Lab 04. Let There Be Macro

Laboratory created by Mateusz Ślażyński for "Programming Language Theory" course at AGH University of Science and Technology in Kraków.

This class focuses at extending Typed Lambda Calculus with various features.
Students are expected to implement:

- `let` expressions allowing to define local variables
- `fix` operator allowing to define recursive functions
- `letrec` macro to clean the recursive function syntax.
  * this task will require implementing a basic macro system 

The "TAPL book" referenced in the source code can be found [here](https://github.com/MPRI/M2-4-2/blob/master/Types%20and%20Programming%20Languages.pdf).

## Lab Instructions

Fill files according to the 'TODO:' comments:

- `./src/semantics/typechecker.py`
- `./src/semantics/evaluator.py`
- `./src/semantics/macro.py`
- `./examples/11_letrec_fibonacci.tl`

## Setup 

* [ ] Make sure, you have a **private** group 
  * [how to create a group](https://docs.gitlab.com/ee/user/group/#create-a-group)
* [ ] Fork this project into your private group
  * [how to create a fork](https://docs.gitlab.com/ee/user/project/repository/forking_workflow.html#creating-a-fork)
* [ ] Add @bobot-is-a-bot as the new project's member (role: **maintainer**)
  * [how to add an user](https://docs.gitlab.com/ee/user/project/members/index.html#add-a-user)
  
## How To Submit Solutions

* [ ] Clone repository: git clone:
    ```bash 
    git clone <repository url>
    ```
* [ ] Solve the exercises 
    * use MiniZincIDE, whatever
* [ ] Commit your changes
    ```bash
    git add <path to the changed files>
    git commit -m <commit message>
    ```
* [ ] Push changes to the gitlab master branch
    ```bash
    git push -u origin master
    ```

The rest will be taken care of automatically. You can check the `GRADE.md` file for your grade / test results. Be aware that it may take some time (up to one hour) till this file appears / gets updated.  



 
