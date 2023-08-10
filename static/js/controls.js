
const version = "Beta 1.0.0";

const navbar = `
<nav class="navbar navbar-dark bg-dark navbar-expand-lg" style="margin-top: 10px;">
        <button class="navbar-dark bg-dark" data-bs-toggle="collapse" type="button" data-bs-target="#navbarDiv">
            <span class="navbar-toggler-icon"> </span>
        </button>

        <div class="navbar-collapse collapse" id="navbarDiv">
            <ul class="navbar-nav">
                <li class="nav-item">
                    <a class="nav-link" href="/">Dashboard</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/agents">Agents</a>
                </li>

                <li class="nav-item dropdown">
                    <div class="dropdown">
                        <a class="nav-link dropdown-toggle" id="navbarDropdown"  data-bs-toggle="dropdown" aria-expanded="false">
                            Jobs
                        </a>
                        <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton1">
                            <li>
                                <a class="dropdown-item" href="/newjob">Create New Job</a>
                            </li>
                            <li>
                                <a class="dropdown-item" href="/jobs">Jobs</a>
                            </li>
                            <li>
                                <a class="dropdown-item" href="/scheduledjobs">Scheduled Jobs</a>
                            </li>
                        </ul>
                    </div>
                </li>
                <li class="nav-item" >
                    <a class="nav-link" href="/streamevents">
                        Events
                        <span class="sr-only"></span>
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/settings">
                        Settings
                        <span class="sr-only"></span>
                    </a>
                </li>
                <li class="nav-item" >
                    <a class="nav-link" href="/logout">
                        Logout
                        <span class="sr-only"></span>
                    </a>
                </li>

            </ul>
        </div>
        <b style="position: absolute; right: 50; z-index: 5;"><label style="color:red;" id="serverTime"></label></b>

        <div aria-live="polite" aria-atomic="true" style="position: absolute; top: 50; right: 0; z-index: 5;">
            <div id="notification-container" style="position: relative; top: 0;"></div>
        </div>
</nav>`;


const banner = `
<div>
    <img src="static/images/ensemble.png" style="width: 200px;">
    <lable>${version}</lable>
</div>`;

const workspaceModal = `
<div class="modal" id="addworkspaceModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">Add New Workspace</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"/>
      </div>
      <div class="modal-body">
        <div class="col">
            <label>Workspace Name</label>
        </div>
        <div class="col">
            <input id="WorkspaceName" type="text"></input>
        </div>
      </div>
      <div class="modal-footer">
        <button onclick="AddWorkspace();" type="button" class="btn btn-primary">Save changes</button>
      </div>
    </div>
  </div>
</div>
`;

let navBar = document.getElementById("nav_element");
if(navBar != undefined)
    navBar.innerHTML = navbar;

let bannerElement = document.getElementById("banner_element");
if(bannerElement != undefined)
    bannerElement.innerHTML = banner;

let workspaceModalElement = document.getElementById("workspace_modal_element");
if(workspaceModalElement != undefined)
    workspaceModalElement.innerHTML = workspaceModal;
