import React from 'react'
import { toast } from 'react-toastify';
import "react-toastify/dist/ReactToastify.css";

// toast.configure()

const create_video_script = async () => {
    let ipt_data = document.getElementById("user_input").value
    if (ipt_data.length > 0) {
        try {
            let res = await fetch("http://127.0.0.1:6200", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: { "user_input": ipt_data }
            })
            if (res.ok) {
                const result = await res.json()
                console.log(result);
            }
        } catch (error) {
            console.log(error)
        }
    } else {
        toast.warning("Please enter proper prompt")
    }
}

export default function User_input() {
    return (
        <>
            <main className='container my-4'>
                <div className="mb-3">
                    <label htmlFor="user_input" className="form-label fs-5">
                        Enter a Query
                    </label>
                    <textarea className="form-control text-muted" id="user_input" rows="3"
                        placeholder='Enter a prompt on which you want to create Video'
                    ></textarea>
                </div>
                <div className='text-center'>
                    <button type="button" className="btn btn-primary"
                        id='btn-generate-script'
                        onClick={create_video_script}>
                        Generate Script for the Video
                    </button>
                </div>
            </main>
        </>
    )
}
