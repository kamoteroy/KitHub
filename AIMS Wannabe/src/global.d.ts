declare module "jspdf" {
	export default class jsPDF {
		constructor(options?: any);
		text(text: string, x: number, y: number): void;
		save(filename?: string): void;
		addPage(): void;
	}
}

declare module "html2canvas";
