
$.getScript('static/js/controls.js');
$.getScript('static/js/message-service.js');

let notificationPollActive = true;

function GetWarningAlert(id, text) {
    return `
    <div id="toast_${id}" class="toast" role="alert" aria-live="assertive" aria-atomic="true" style="z-index: 5;" data-delay="5000">
        <div class="toast-header">
            <div class="rounded me-2 bg-danger" style="height:10px; width:10px"></div>
            <strong class="me-auto">Alert</strong>
            <button onclick="DissmissAlert(${id})" type="button" class="btn-close p-2" data-bs-dismiss="toast" aria-label="Close"/>
        </div>
        <div class="toast-body">
            ${text}
        </div>
    </div>
    `
}

function GetNotificationAlert(id, text) {
    return `
    <div id="toast_${id}" class="toast" role="alert" aria-live="assertive" aria-atomic="true" style="z-index: 5;" data-delay="5000">
        <div class="toast-header">
            <div class="rounded me-2 bg-success" style="height:10px; width:10px"></div>
            <strong class="me-auto">Notification</strong>
            <button onclick="DissmissAlert(${id})" type="button" class="btn-close p-2" data-bs-dismiss="toast" aria-label="Close"/>
        </div>
        <div class="toast-body">
            ${text}
        </div>
    </div>
    `
}

function GetInformationAlert(id, text) {
    return `
    <div id="toast_${id}" class="toast" role="alert" aria-live="assertive" aria-atomic="true" style="z-index: 5;" data-delay="5000">
        <div class="toast-header">
            <div class="rounded me-2 bg-primary" style="height:10px; width:10px"></div>
            <strong class="me-auto">Information</strong>
            <button onclick="DissmissAlert(${id})" type="button" class="btn-close  p-2" data-bs-dismiss="toast" aria-label="Close"/>
        </div>
        <div class="toast-body">
            ${text}
        </div>
    </div>
    `
}

function CheckMessages() {
    if (!notificationPollActive)
        return;

    $.ajax({
        url: '/messages',
        method: 'GET',
        success: function (res, textStatus, data) {
            JSON.parse(data.responseText).forEach(element => {
                let existingAlert = $(`#toast_${element.Id}`)[0];
                if (existingAlert == undefined) {

                    if (element.MessageType === 0) {
                        $("#notification-container").append(GetInformationAlert(element.Id, element.Message));
                    }
                    else if (element.MessageType === 1) {
                        $("#notification-container").append(GetWarningAlert(element.Id, element.Message));
                    }
                    else if (element.MessageType === 2) {
                        $("#notification-container").append(GetNotificationAlert(element.Id, element.Message));
                    }

                    $(`#toast_${element.Id}`).on('hidden.bs.toast', function () {
                        DissmissAlert(element.Id);
                        $(`#toast_${element.Id}`).remove();
                    });
                    $(`#toast_${element.Id}`).toast('show');
                }
            });
        }
    })
    setTimeout(CheckMessages, 3000);
}

function DissmissAlert(id) {
    $.ajax({
        url: `/messages?dismiss=${id}`,
        method: 'GET',
        success: function (res, textStatus, data) { }
    }
    );
}

function AddWorkspace() {
    $("#addworkspaceModal").modal('toggle');

    $.ajax({
        url: `/workspace?id=${encodeURIComponent($("#WorkspaceName").val())}`,
        method: 'GET',
        success: function (res, textStatus, data) {
            window.location.href = "/";
        }
    });
}

function DisableNotificationPolling() {
    notificationPollActive = false;
}

function MakeApiEndpointRequest(endpoint, method, callback) {
    $.ajax({
        url: endpoint,
        type: method,
        success: function (res, textStatus, data) {
            callback(data);
        }
    });
}

function MakeApiJsonPostRequest(endpoint, callback, postData, errorCallback){
    $.ajax({
        url: endpoint,
        type: 'POST',
        data: postData,
        dataType: 'json',
        contentType: "application/json",
        success: function (res, textStatus, data) {
            callback(data);
        },
        error: function (res, textStatus, data){
            errorCallback();
        }
    });
}

function RegisterApiEndpointPoll(endpoint, method, callback, frequency) {
    setTimeout(() => {
        MakeApiEndpointRequest(endpoint, method, callback);
        RegisterApiEndpointPoll(endpoint, method, callback, frequency);
    }, frequency);
}

function UpdateServerTime(){
    MakeApiEndpointRequest("/api/getTime","GET",(res,status,data)=>{
        $("#serverTime").text(`SERVER TIME: ${res.responseText}`);
        setTimeout(UpdateServerTime, 3000)
    });
}

setTimeout(CheckMessages, 3000);
setTimeout(UpdateServerTime, 3000)