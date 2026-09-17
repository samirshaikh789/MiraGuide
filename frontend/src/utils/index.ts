export function copyText(text: string) { return navigator.clipboard?.writeText(text); }
export function fileIsImage(file: File) { return file.type.startsWith('image/'); }
export function fileIsSmallEnough(file: File, maxSize = 8 * 1024 * 1024) { return file.size <= maxSize; }