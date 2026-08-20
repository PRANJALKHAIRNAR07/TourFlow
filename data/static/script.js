const form = document.getElementById("recommendForm");

const result = document.getElementById("result");

const resultContent = document.getElementById("resultContent");


form.addEventListener("submit", async function (event) {

    event.preventDefault();

    const destinationId =
        document.getElementById("destination").value;

    const date =
        document.getElementById("date").value;

    const preferredTime =
        document.getElementById("preferred_time").value;


    if (!destinationId || !date) {

        alert("Please select a destination and date.");

        return;
    }


    try {

        const response = await fetch("/api/recommend", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                destination_id: destinationId,
                date: date,
                preferred_time: preferredTime

            })

        });


        const data = await response.json();


        if (!data.success) {

            alert(data.message);

            return;
        }


        const best = data.recommended_slot;

        let preferredHTML = "";


        if (data.preferred_result) {

            const preferred =
                data.preferred_result;

            let crowdClass =
                "crowd-low";

            if (preferred.level === "high") {
                crowdClass = "crowd-high";
            }
            else if (preferred.level === "medium") {
                crowdClass = "crowd-medium";
            }


            preferredHTML = `

                <div class="recommendation">

                    <h3>Your Preferred Slot</h3>

                    <p>
                        Time:
                        <strong>
                            ${data.preferred_time}
                        </strong>
                    </p>

                    <p>
                        Expected Visitors:
                        <strong>
                            ${preferred.expected_visitors}
                        </strong>
                    </p>

                    <p>
                        Capacity:
                        <strong>
                            ${preferred.capacity}
                        </strong>
                    </p>

                    <p>
                        Status:
                        <span class="${crowdClass}">
                            ${preferred.status}
                        </span>
                    </p>

                </div>
            `;
        }


        resultContent.innerHTML = `

            <p>
                Destination:
                <strong>
                    ${data.destination}
                </strong>
            </p>

            <p>
                Visit Date:
                <strong>
                    ${data.date}
                </strong>
            </p>


            <div class="recommendation">

                <h3>
                    ${best.time}
                </h3>

                <p>
                    🟢 Recommended Time Slot
                </p>

                <p>
                    Expected Visitors:
                    <strong>
                        ${best.expected_visitors}
                    </strong>
                </p>

                <p>
                    Capacity Utilization:
                    <strong>
                        ${best.utilization}%
                    </strong>
                </p>

            </div>

            ${preferredHTML}


            <div class="slot-list">

                <h3>
                    Available Time Slots
                </h3>

                ${data.all_slots.map(slot => `

                    <div class="slot">

                        <span>
                            ${slot.time}
                        </span>

                        <span>
                            ${slot.expected_visitors} visitors
                        </span>

                        <strong>
                            ${slot.category}
                        </strong>

                    </div>

                `).join("")}

            </div>

        `;


        result.classList.remove("hidden");

        result.scrollIntoView({
            behavior: "smooth"
        });


    }
    catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the TourFlow server."
        );

    }

});
