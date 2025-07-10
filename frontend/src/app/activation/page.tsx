import ActivationFlow from '@/components/activation/ActivationFlow';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

export default function ActivationPage() {
    return (
        <main className="container mx-auto p-4 md:p-8">
            <Card className="max-w-3xl mx-auto">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold text-center">AI File Analyzer</CardTitle>
                    <CardDescription className="text-center">
                        Upload your files and see how an AI teammate can analyze your workflows in seconds.
                    </CardDescription>
                </CardHeader>
                <ActivationFlow />
            </Card>
        </main>
    );
}