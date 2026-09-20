let recordedBlob=null,mediaRecorder=null,chunks=[];
const $=id=>document.getElementById(id);

$("recordBtn").onclick=async()=>{
  if(mediaRecorder&&mediaRecorder.state==="recording"){
    mediaRecorder.stop(); $("recordBtn").textContent="● Start microphone"; return;
  }
  try{
    const stream=await navigator.mediaDevices.getUserMedia({audio:true});
    chunks=[]; mediaRecorder=new MediaRecorder(stream);
    mediaRecorder.ondataavailable=e=>chunks.push(e.data);
    mediaRecorder.onstop=()=>{
      recordedBlob=new Blob(chunks,{type:"audio/webm"});
      stream.getTracks().forEach(t=>t.stop());
      $("recordStatus").textContent="Recording ready. Click Transcribe + Translate.";
    };
    mediaRecorder.start();
    $("recordBtn").textContent="■ Stop recording";
    $("recordStatus").textContent="Recording…";
  }catch(e){$("recordStatus").textContent="Microphone permission was not granted."}
};

$("runBtn").onclick=async()=>{
  const file=$("audioFile").files[0]||recordedBlob;
  if(!file){$("progress").textContent="Please choose an audio/video file or record your voice.";return}
  $("runBtn").disabled=true; $("progress").textContent="Transcribing…";
  try{
    const fd=new FormData();
    fd.append("file",file,file.name||"recording.webm");
    const r=await fetch("/api/transcribe",{method:"POST",body:fd});
    const d=await r.json();
    if(!r.ok)throw Error(d.detail||d.error||"Transcription failed");
    $("original").textContent=d.text;
    $("progress").textContent="Transcribed. Translating…";

    const tr=await fetch("/api/translate",{
      method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({text:d.text,targetLanguage:$("targetLang").value})
    });
    const td=await tr.json();
    if(!tr.ok)throw Error(td.detail||td.error||"Translation failed");
    $("translation").textContent=td.translation;
    $("progress").textContent="Done ✓";
  }catch(e){$("progress").textContent=e.message}
  finally{$("runBtn").disabled=false}
};

$("speakBtn").onclick=async()=>{
  const text=$("translation").textContent;
  if(!text||text.startsWith("Your translation"))return;
  $("speakBtn").disabled=true; $("speakBtn").textContent="Generating…";
  try{
    const r=await fetch("/api/speak",{
      method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({text})
    });
    if(!r.ok){
      const d=await r.json().catch(()=>({}));
      throw Error(d.detail||d.error||"Voice generation failed");
    }
    const blob=await r.blob();
    $("player").src=URL.createObjectURL(blob);
    $("player").hidden=false;
  }catch(e){alert(e.message)}
  finally{$("speakBtn").disabled=false;$("speakBtn").textContent="🔊 Generate voice"}
};

$("copyOriginal").onclick=()=>navigator.clipboard.writeText($("original").textContent);
$("copyTranslation").onclick=()=>navigator.clipboard.writeText($("translation").textContent);
